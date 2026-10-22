from fastapi import APIRouter
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.documents import router as documents_router
from app.api.v1.routes.conversations import router as conversations_router
from app.api.v1.routes.qa import router as qa_router
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(documents_router)
api_router.include_router(conversations_router)
api_router.include_router(qa_router)
