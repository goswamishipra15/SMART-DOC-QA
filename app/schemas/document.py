from pydantic import BaseModel, ConfigDict
from typing import Optional
class DocumentCreateResponse(BaseModel): document_id: str; job_id: str; status: str
class DocumentStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; filename: str; file_type: str; status: str; progress: int; error_message: Optional[str] = None
class ChunkResponse(BaseModel): id: str; chunk_index: int; page_number: Optional[int]; chunk_text: str; token_count: int
class ProgressResponse(BaseModel): document_id: str; status: str; progress: int; step: str; error_message: Optional[str] = None
