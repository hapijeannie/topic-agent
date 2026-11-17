import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
import psycopg

from topic_agent.documents import get_document, list_documents, prepare_document
from topic_agent.storage import save_document
from topic_agent.auth import configure_auth, require_owner


class ImportBody(BaseModel):
    raw: str
    source_namespace: str
    ownership: str
    source_path: str = "upload"


def health():
    return {
        "status": "ok"
    }


def open_connection():
    load_dotenv(Path(__file__).resolve().with_name(".env.local"), override=False)
    database_url = os.getenv("DATABASE_URL")
    if not database_url or not database_url.strip():
        raise HTTPException(status_code=503, detail="Database is not configured.")
    try:
        return psycopg.connect(database_url.strip(), autocommit=True, connect_timeout=10)
    except (psycopg.Error, OSError):
        raise HTTPException(status_code=503, detail="Database connection failed.") from None


def create_document(body: ImportBody):
    try:
        document, chunks = prepare_document(
            body.raw, body.source_namespace, body.ownership, body.source_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    try:
        with open_connection() as connection:
            return save_document(connection, document, chunks, body.source_path)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except psycopg.Error:
        raise HTTPException(status_code=500, detail="Import failed.") from None


def read_documents(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    try:
        with open_connection() as connection:
            return list_documents(connection, limit, offset)
    except psycopg.Error:
        raise HTTPException(status_code=500, detail='Could not load documents.') from None


def read_document(article_id: int):
    if article_id <= 0:
        raise HTTPException(status_code=404, detail='Document not found.')
    try:
        with open_connection() as connection:
            result = get_document(connection, article_id)
    except psycopg.Error:
        raise HTTPException(status_code=500, detail='Could not load document.') from None
    if result is None:
        raise HTTPException(status_code=404, detail='Document not found.')
    return result


def create_app(settings=None):
    if settings is None:
        load_dotenv(Path(__file__).resolve().with_name('.env.local'), override=False)
        settings = dict(os.environ)
    application = FastAPI()
    configure_auth(application, settings)
    protected = [Depends(require_owner)]
    application.add_api_route('/health', health, methods=['GET'])
    application.add_api_route('/documents', create_document, methods=['POST'], dependencies=protected)
    application.add_api_route('/documents', read_documents, methods=['GET'], dependencies=protected)
    application.add_api_route('/documents/{article_id}', read_document, methods=['GET'], dependencies=protected)
    return application


app = create_app()
