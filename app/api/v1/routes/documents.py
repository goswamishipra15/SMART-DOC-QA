from __future__ import annotations
from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import get_db
from app.db.models.document import Document, DocumentStatus
from app.db.models.job import IngestionJob
from app.db.models.chunk import DocumentChunk
from app.schemas.document import DocumentCreateResponse, DocumentStatusResponse, ProgressResponse, ChunkResponse
from app.tasks.ingest import ingest_document
from app.utils.file_validation import is_allowed_file
router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()
@router.post("", response_model=DocumentCreateResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not is_allowed_file(file.filename or ""): raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
    upload_dir = Path(settings.upload_dir); upload_dir.mkdir(parents=True, exist_ok=True)
    document_id = str(uuid.uuid4()); storage_path = upload_dir / f"{document_id}_{file.filename}"; content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024: raise HTTPException(status_code=400, detail=f"File exceeds max size of {settings.max_upload_mb} MB")
    storage_path.write_bytes(content)
    doc = Document(id=document_id, filename=file.filename, file_type=Path(file.filename).suffix.lower().lstrip('.'), storage_path=str(storage_path), status=DocumentStatus.PENDING, progress=0)
    job = IngestionJob(document_id=document_id, job_status="QUEUED"); db.add(doc); db.add(job); db.commit(); celery_result = ingest_document.delay(document_id); return DocumentCreateResponse(document_id=document_id, job_id=celery_result.id, status="QUEUED")
@router.get("/{document_id}", response_model=DocumentStatusResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first();
    if not doc: raise HTTPException(status_code=404, detail="Document not found")
    return doc
@router.get("/{document_id}/progress", response_model=ProgressResponse)
def get_progress(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first();
    if not doc: raise HTTPException(status_code=404, detail="Document not found")
    step = "queued" if doc.status == DocumentStatus.PENDING else doc.status.value.lower(); return ProgressResponse(document_id=document_id, status=doc.status.value, progress=doc.progress, step=step, error_message=doc.error_message)
@router.get("/{document_id}/chunks", response_model=list[ChunkResponse])
def get_chunks(document_id: str, db: Session = Depends(get_db)):
    rows = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index.asc()).all(); return [ChunkResponse(id=r.id, chunk_index=r.chunk_index, page_number=r.page_number, chunk_text=r.chunk_text, token_count=r.token_count) for r in rows]
