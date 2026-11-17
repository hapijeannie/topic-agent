import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fastapi import HTTPException
import psycopg

import main
from topic_agent.documents import prepare_document


SAMPLE = (Path(__file__).resolve().parent / "fixtures/chunk_preview/sample.md").read_text()


class DocumentRouteTests(unittest.TestCase):
    def body(self, **changes):
        values = {
            "raw": SAMPLE,
            "source_namespace": "demo",
            "ownership": "owned",
            "source_path": "sample.md",
        }
        values.update(changes)
        return main.ImportBody(**values)

    def test_invalid_markdown_is_400_before_database(self):
        with patch.object(main, "open_connection", side_effect=AssertionError("should not connect")):
            with self.assertRaises(HTTPException) as caught:
                main.create_document(self.body(raw="not markdown"))
        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(caught.exception.detail, "缺少完整的 Frontmatter 起止标记")

    def test_blank_source_path_is_400(self):
        with self.assertRaises(HTTPException) as caught:
            main.create_document(self.body(source_path="  "))
        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(caught.exception.detail, "必须提供来源路径")

    def test_import_returns_storage_result_for_two_chunks(self):
        class Connection:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

        stored = {"status": "imported", "article_id": 7, "chunk_count": 2}
        with patch.object(main, "open_connection", return_value=Connection()), \
             patch.object(main, "save_document", return_value=stored) as save:
            result = main.create_document(self.body())
        self.assertEqual(result, stored)
        connection, document, chunks, source_path = save.call_args.args
        self.assertIsInstance(connection, Connection)
        prepared, prepared_chunks = prepare_document(SAMPLE, "demo", "owned", "sample.md")
        self.assertEqual(document, prepared)
        self.assertEqual(chunks, prepared_chunks)
        self.assertEqual(source_path, "sample.md")
        self.assertEqual(len(chunks), 2)

    def test_duplicate_passes_through(self):
        class Connection:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

        stored = {"status": "duplicate", "article_id": 7, "chunk_count": 2}
        with patch.object(main, "open_connection", return_value=Connection()), \
             patch.object(main, "save_document", return_value=stored):
            self.assertEqual(main.create_document(self.body())["status"], "duplicate")

    def test_missing_database_is_503(self):
        previous = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = " "
        try:
            with self.assertRaises(HTTPException) as caught:
                main.create_document(self.body())
        finally:
            if previous is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = previous
        self.assertEqual(caught.exception.status_code, 503)
        self.assertEqual(caught.exception.detail, "Database is not configured.")

    def test_database_error_hides_details(self):
        class Connection:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

        with patch.object(main, "open_connection", return_value=Connection()), \
             patch.object(main, "save_document", side_effect=psycopg.OperationalError("password=secret")):
            with self.assertRaises(HTTPException) as caught:
                main.create_document(self.body())
        self.assertEqual(caught.exception.status_code, 500)
        self.assertEqual(caught.exception.detail, "Import failed.")
        self.assertNotIn("secret", caught.exception.detail)
