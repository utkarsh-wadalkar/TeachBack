from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.curriculum import CurriculumTree
from app.services import curriculum_service

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.get("", response_model=CurriculumTree)
def get_curriculum(db: Session = Depends(get_db)) -> CurriculumTree:
    """The full academic tree (university -> ... -> concept) with mastery scores."""
    return curriculum_service.build_tree(db)
