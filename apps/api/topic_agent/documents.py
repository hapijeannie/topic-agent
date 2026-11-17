"""把一篇 Markdown 准备成可保存的文章和分块。不打开数据库连接。"""

from .chunking import chunk_body
from .ingestion import parse_markdown
from psycopg.rows import dict_row

DEFAULT_MAX_CHARS = 1000


def prepare_document(raw, source_namespace, ownership, source_path, max_chars=DEFAULT_MAX_CHARS):
    if not isinstance(source_path, str) or not source_path.strip():
        raise ValueError('必须提供来源路径')
    document = parse_markdown(raw, source_namespace, ownership)
    chunks = chunk_body(document.body, max_chars)
    return document, chunks


def list_documents(conn, limit=20, offset=0):
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            '''SELECT a.id, a.title, a.source_namespace, a.source_id, a.ownership,
                      a.created_at, (SELECT count(*) FROM public.chunks c WHERE c.article_id = a.id) AS chunk_count
               FROM public.articles a ORDER BY a.created_at DESC, a.id DESC LIMIT %s OFFSET %s''',
            (limit + 1, offset),
        )
        rows = cursor.fetchall()
    return {'items': rows[:limit], 'has_more': len(rows) > limit}


def get_document(conn, article_id):
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            '''SELECT a.id, a.title, a.source_namespace, a.source_id, a.ownership,
                      a.source_path, a.body, a.metadata, a.created_at,
                      COALESCE((SELECT jsonb_agg(jsonb_build_object(
                          'index', c.chunk_index, 'text', c.text) ORDER BY c.chunk_index)
                          FROM public.chunks c WHERE c.article_id = a.id), '[]'::jsonb) AS chunks
               FROM public.articles a WHERE a.id = %s''', (article_id,),
        )
        return cursor.fetchone()
