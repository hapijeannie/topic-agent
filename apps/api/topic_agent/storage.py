"""Save parsed articles and their chunks atomically; never create tables."""

from psycopg.types.json import Jsonb


def save_document(conn, doc, chunks, source_path):
    """Use an idle autocommit connection for a committed result.

    Inside an existing transaction this creates a savepoint; the caller then
    owns the final commit. Exceptions propagate so the entire article rolls back.
    """
    if not chunks:
        raise ValueError('文章必须包含至少一个分块')
    with conn.transaction():
        with conn.cursor() as cursor:
            # Let the unique constraint arbitrate identity, including simultaneous inserts.
            cursor.execute(
                '''INSERT INTO public.articles
                   (source_namespace, source_id, ownership, title, source_path,
                    raw, body, metadata, content_hash)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (source_namespace, source_id) DO NOTHING
                   RETURNING id''',
                (doc.source_namespace, doc.source_id, doc.ownership, doc.title,
                 str(source_path), doc.raw, doc.body, Jsonb(doc.metadata), doc.content_hash),
            )
            inserted = cursor.fetchone()
            if inserted is None:
                cursor.execute(
                    '''SELECT a.id, a.content_hash
                       FROM public.articles a
                       WHERE a.source_namespace = %s AND a.source_id = %s
                       FOR UPDATE OF a''',
                    (doc.source_namespace, doc.source_id),
                )
                article_id, previous_hash = cursor.fetchone()
                if previous_hash == doc.content_hash:
                    cursor.execute('SELECT count(*) FROM public.chunks WHERE article_id = %s', (article_id,))
                    chunk_count = cursor.fetchone()[0]
                    return {'status': 'duplicate', 'article_id': article_id, 'chunk_count': chunk_count}
                cursor.execute(
                    '''UPDATE public.articles SET ownership = %s, title = %s,
                       source_path = %s, raw = %s, body = %s, metadata = %s,
                       content_hash = %s WHERE id = %s''',
                    (doc.ownership, doc.title, str(source_path), doc.raw, doc.body,
                     Jsonb(doc.metadata), doc.content_hash, article_id),
                )
                cursor.execute('DELETE FROM public.chunks WHERE article_id = %s', (article_id,))
                status = 'updated'
            else:
                article_id = inserted[0]
                status = 'imported'
            cursor.executemany(
                'INSERT INTO public.chunks (article_id, chunk_index, text) VALUES (%s, %s, %s)',
                [(article_id, chunk['index'], chunk['text']) for chunk in chunks],
            )
            chunk_count = len(chunks)
    return {'status': status, 'article_id': article_id, 'chunk_count': chunk_count}
