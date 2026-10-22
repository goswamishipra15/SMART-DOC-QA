from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.conversation import Conversation
from app.schemas.conversation import ConversationCreateRequest, ConversationResponse
router = APIRouter(prefix="/conversations", tags=["conversations"])
@router.post("", response_model=ConversationResponse)
def create_conversation(payload: ConversationCreateRequest, db: Session = Depends(get_db)):
    convo = Conversation(document_id=payload.document_id, title=payload.title); db.add(convo); db.commit(); db.refresh(convo); return convo
@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter(Conversation.id == conversation_id).first();
    if not convo: raise HTTPException(status_code=404, detail="Conversation not found")
    return convo
