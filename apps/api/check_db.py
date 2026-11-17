"""Check PostgreSQL connectivity without modifying data or printing credentials."""

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import psycopg


def main():
    try:
        load_dotenv(Path(__file__).resolve().with_name(".env.local"), override=False)
        database_url = os.getenv("DATABASE_URL")
        if not database_url or not database_url.strip():
            print("DATABASE_URL is not configured.", file=sys.stderr)
            return 1

        with psycopg.connect(database_url, connect_timeout=10, autocommit=True) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
    except (psycopg.Error, OSError, ValueError):
        # Driver errors can contain connection details; never print the exception.
        print("Database connection check failed. Check configuration and network access.", file=sys.stderr)
        return 1

    if result != (1,):
        print("Database check returned an unexpected result.", file=sys.stderr)
        return 1

    print("Database connection successful.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
