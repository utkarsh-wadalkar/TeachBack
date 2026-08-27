from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.curriculum import LearningContent
from app.services import learning_service

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/{concept_id}", response_model=LearningContent)
def get_learning(concept_id: int, db: Session = Depends(get_db)) -> LearningContent:
    """Reading content + breadcrumb + sibling concepts for a single concept."""
    return learning_service.get_learning_content(db, concept_id)
