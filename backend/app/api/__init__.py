"""Aggregates every route module into a single API router mounted at ``/api``."""

from fastapi import APIRouter

from app.api import curriculum, health, learning, pyq, teachback

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(curriculum.router)
api_router.include_router(learning.router)
api_router.include_router(teachback.router)
api_router.include_router(pyq.router)
