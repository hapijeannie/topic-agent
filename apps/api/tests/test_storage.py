"""Opt-in PostgreSQL checks; test rows are rolled back, identity sequences may advance."""

from dataclasses import replace
import os
from pathlib import Path
import unittest
from uuid import uuid4

from dotenv import dotenv_values
import psycopg

from topic_agent.chunking import chunk_body
from topic_agent.ingestion import parse_markdown
from topic_agent.storage import save_document
from topic_agent.documents import get_document, list_documents


@unittest.skipUnless(os.getenv('RUN_DB_TESTS') == '1', 'set RUN_DB_TESTS=1 for database checks')
class StorageTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        url = dotenv_values(root / '.env.local').get('DATABASE_URL')
        if not url:
            self.fail('DATABASE_URL is not configured')
        try:
            self.conn = psycopg.connect(url, autocommit=True, connect_timeout=10)
        except psycopg.Error:
            self.fail('Database connection failed; details suppressed')
        self.addCleanup(self.conn.close)
        self.enterContext(self.conn.transaction(force_rollback=True))
        self.conn.execute("SET LOCAL statement_timeout = '15s'")
        self.source = 'storage-test-' + uuid4().hex
        raw = (root / 'tests/fixtures/chunk_preview/sample.md').read_bytes().decode('utf-8')
        self.doc = parse_markdown(raw, self.source, 'owned')
        self.chunks = chunk_body(self.doc.body, 1000)

    def test_import_duplicate_then_replace_article_and_chunks(self):
        result = save_document(self.conn, self.doc, self.chunks, 'sample.md')
        self.assertEqual(result['status'], 'imported')
        self.assertEqual(result['chunk_count'], 2)
        article_id = result['article_id']
        row = self.conn.execute('SELECT raw, metadata FROM public.articles WHERE id = %s', (article_id,)).fetchone()
        self.assertEqual(row, (self.doc.raw, self.doc.metadata))
        texts = self.conn.execute('SELECT text FROM public.chunks WHERE article_id = %s ORDER BY chunk_index', (article_id,)).fetchall()
        self.assertEqual(''.join(row[0] for row in texts), self.doc.body)
        duplicate = save_document(self.conn, self.doc, self.chunks, 'sample.md')
        self.assertEqual(duplicate, dict(result, status='duplicate'))
        changed = parse_markdown('---\ntitle: 新标题\nslug: chunk-demo\n---\n只有一块\n', self.source, 'reference')
        updated = save_document(self.conn, changed, chunk_body(changed.body, 1000), 'new.md')
        self.assertEqual(updated, dict(result, status='updated', chunk_count=1))
        row = self.conn.execute('SELECT raw, title, ownership, source_path FROM public.articles WHERE id = %s', (article_id,)).fetchone()
        self.assertEqual(row, (changed.raw, changed.title, 'reference', 'new.md'))
        texts = self.conn.execute('SELECT text FROM public.chunks WHERE article_id = %s ORDER BY chunk_index', (article_id,)).fetchall()
        self.assertEqual(texts, [(changed.body,)])

    def test_update_failure_restores_original_article_and_chunks(self):
        first = save_document(self.conn, self.doc, self.chunks, 'sample.md')
        before = self.conn.execute('SELECT id, text FROM public.chunks WHERE article_id = %s ORDER BY chunk_index', (first['article_id'],)).fetchall()
        changed = parse_markdown(self.doc.raw + 'changed', self.source, 'owned')
        with self.assertRaises(psycopg.Error):
            save_document(self.conn, changed, [dict(self.chunks[0], text='\x00')], 'new.md')
        self.assertEqual(self.conn.execute('SELECT raw, source_path FROM public.articles WHERE id = %s', (first['article_id'],)).fetchone(), (self.doc.raw, 'sample.md'))
        self.assertEqual(self.conn.execute('SELECT id, text FROM public.chunks WHERE article_id = %s ORDER BY chunk_index', (first['article_id'],)).fetchall(), before)

    def test_chunk_failure_rolls_back_article_and_prior_chunks(self):
        # A NUL cannot be stored in PostgreSQL text; the second chunk fails after insertion starts.
        bad_chunks = [self.chunks[0], dict(self.chunks[1], text='\x00')]
        with self.assertRaises(psycopg.Error):
            save_document(self.conn, self.doc, bad_chunks, 'sample.md')
        self.assertEqual(self.conn.execute('SELECT count(*) FROM public.articles WHERE source_namespace = %s', (self.source,)).fetchone()[0], 0)
        result = save_document(self.conn, self.doc, self.chunks, 'sample.md')
        self.assertEqual(result['status'], 'imported')

    def test_same_source_id_in_other_namespace_is_new_article(self):
        first = save_document(self.conn, self.doc, self.chunks, 'sample.md')
        other = replace(self.doc, source_namespace=self.source + '-other')
        second = save_document(self.conn, other, self.chunks, 'sample.md')
        self.assertEqual(second['status'], 'imported')
        self.assertNotEqual(first['article_id'], second['article_id'])

    def test_list_detail_and_missing_article(self):
        result = save_document(self.conn, self.doc, self.chunks, 'sample.md')
        listing = list_documents(self.conn, limit=1)
        self.assertEqual(len(listing['items']), 1)
        self.assertEqual(listing['items'][0]['id'], result['article_id'])
        self.assertNotIn('body', listing['items'][0])
        detail = get_document(self.conn, result['article_id'])
        self.assertEqual(detail['body'], self.doc.body)
        self.assertEqual(detail['chunks'], [{'index': c['index'], 'text': c['text']} for c in self.chunks])
        self.assertIsNone(get_document(self.conn, -1))
        self.assertEqual(list_documents(self.conn, offset=2147483647), {'items': [], 'has_more': False})
