from __future__ import annotations
from sqlalchemy.orm import Session
from app.db.models.chunk import DocumentChunk
from app.services.ingestion.embeddings import embed_texts
from app.services.ingestion.vector_store import FaissStore
from app.services.ingestion.bm25_store import BM25Store

def build_indexes(db: Session, document_id: str) -> None:
    chunk_rows = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index.asc()).all()
    chunks = [{"id": row.id, "document_id": row.document_id, "chunk_index": row.chunk_index, "page_number": row.page_number, "chunk_text": row.chunk_text, "token_count": row.token_count} for row in chunk_rows]
    vectors = embed_texts([c["chunk_text"] for c in chunks])
    metadata = [{"chunk_id": c["id"], "page_number": c["page_number"], "text": c["chunk_text"], "chunk_index": c["chunk_index"]} for c in chunks]
    FaissStore(document_id).save(vectors, metadata)
    BM25Store(document_id).save(chunks)
