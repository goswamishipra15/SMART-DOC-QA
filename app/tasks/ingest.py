from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from app.tasks.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models.document import Document, DocumentStatus
from app.db.models.chunk import DocumentChunk
from app.db.models.job import IngestionJob
from app.services.ingestion.parser import extract_document
from app.services.ingestion.chunker import chunk_pages
from app.services.ingestion.index_manager import build_indexes
@celery_app.task(name="ingest_document")
def ingest_document(document_id: str) -> dict:
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc: raise ValueError("Document not found")
        job = db.query(IngestionJob).filter(IngestionJob.document_id == document_id).first() or IngestionJob(document_id=document_id, job_status="RUNNING", started_at=datetime.utcnow())
        db.add(job); doc.status = DocumentStatus.PROCESSING; doc.progress = 5; db.commit()
        pages = extract_document(doc.storage_path); doc.progress = 25; db.commit()
        chunks = chunk_pages(pages); doc.progress = 45; db.commit()
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete(); db.commit()
        for ch in chunks: db.add(DocumentChunk(document_id=document_id, chunk_index=ch.chunk_index, page_number=ch.page_number, chunk_text=ch.text, token_count=ch.token_count))
        db.commit(); doc.progress = 70; db.commit(); build_indexes(db, document_id); doc.progress = 95; db.commit(); doc.status = DocumentStatus.READY; doc.progress = 100; job.job_status = "SUCCESS"; job.finished_at = datetime.utcnow(); db.commit(); return {"document_id": document_id, "status": "SUCCESS"}
    except Exception as exc:
        db.rollback(); doc = db.query(Document).filter(Document.id == document_id).first();
        if doc: doc.status = DocumentStatus.FAILED; doc.error_message = str(exc); doc.progress = 0
        job = db.query(IngestionJob).filter(IngestionJob.document_id == document_id).first()
        if job: job.job_status = "FAILED"; job.finished_at = datetime.utcnow(); job.error_message = str(exc)
        db.commit(); raise
    finally:
        db.close()
