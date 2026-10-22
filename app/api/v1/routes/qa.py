from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.document import Document, DocumentStatus
from app.schemas.qa import AskRequest, AskResponse
from app.services.qa.answer_service import ask_question
router = APIRouter(tags=["qa"])
@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == payload.document_id).first()
    if not doc: raise HTTPException(status_code=404, detail="Document not found")
    if doc.status != DocumentStatus.READY: raise HTTPException(status_code=409, detail=f"Document is not ready. Current status: {doc.status.value}")
    return ask_question(db, payload.document_id, payload.question, payload.conversation_id)
