from typing import Optional
from pydantic import BaseModel
class AskRequest(BaseModel): document_id: str; question: str; conversation_id: Optional[str] = None
class SourceChunk(BaseModel): chunk_id: str; page_number: Optional[int] = None; score: float; text: str
class AskResponse(BaseModel): answer: str; document_id: str; conversation_id: Optional[str] = None; answer_type: str; confidence: float; sources: list[SourceChunk] = []
