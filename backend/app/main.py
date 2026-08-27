"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.config import settings
from app.core.errors import AppError
from app.db.base import Base
from app.db.session import engine

# Import models so every table is registered on Base.metadata before create_all.
import app.db.models  # noqa: F401,E402


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="TeachBack — AI that determines whether a student genuinely understands.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.on_event("startup")
    def _ensure_schema() -> None:
        # Create tables if they don't exist. Demo *data* is loaded separately via
        # scripts/load_data.py — this only guarantees the schema is present.
        Base.metadata.create_all(bind=engine)

    @app.get("/", tags=["root"])
    def root() -> dict:
        return {"app": settings.app_name, "docs": "/docs", "health": "/api/health"}

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
