"""Import only the repository's synthetic sample; a manual storage acceptance command."""

import json
from pathlib import Path
import sys

from dotenv import dotenv_values
import psycopg

from topic_agent.chunking import chunk_body
from topic_agent.ingestion import parse_markdown
from topic_agent.storage import save_document


def main():
    root = Path(__file__).resolve().parent
    try:
        # Use this project's explicit local target, not an unrelated shell connection.
        url = dotenv_values(root / '.env.local').get('DATABASE_URL')
        if not url:
            print('DATABASE_URL is not configured.', file=sys.stderr)
            return 1
        sample = root / 'tests/fixtures/chunk_preview/sample.md'
        doc = parse_markdown(sample.read_bytes().decode('utf-8'), 'storage-demo', 'owned')
        chunks = chunk_body(doc.body, 1000)
        with psycopg.connect(url, autocommit=True, connect_timeout=10) as conn:
            result = save_document(conn, doc, chunks, 'tests/fixtures/chunk_preview/sample.md')
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (psycopg.Error, OSError, ValueError):
        print('Sample import failed. Check configuration, network and schema.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
