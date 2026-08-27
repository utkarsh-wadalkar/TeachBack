from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.env,
        "llm_provider": settings.llm_provider,
        "stt_provider": settings.stt_provider,
        "retriever_backend": settings.retriever_backend,
    }
