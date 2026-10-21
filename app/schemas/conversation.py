from pydantic import BaseModel, ConfigDict
from typing import Optional
class ConversationCreateRequest(BaseModel): document_id: str; title: Optional[str] = None
class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; document_id: str; title: Optional[str] = None
