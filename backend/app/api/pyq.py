from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.pyq import PyqAttemptRequest, PyqAttemptResponse, PyqOut
from app.services import pyq_service

router = APIRouter(prefix="/pyq", tags=["pyq"])


@router.get("/concepts/{concept_id}", response_model=list[PyqOut])
def list_pyqs(concept_id: int, db: Session = Depends(get_db)) -> list[PyqOut]:
    return pyq_service.list_for_concept(db, concept_id)


@router.get("/{pyq_id}", response_model=PyqOut)
def get_pyq(pyq_id: int, db: Session = Depends(get_db)) -> PyqOut:
    return pyq_service.get_pyq_out(db, pyq_id)


@router.post("/{pyq_id}/attempts", response_model=PyqAttemptResponse)
def attempt_pyq(
    pyq_id: int, body: PyqAttemptRequest, db: Session = Depends(get_db)
) -> PyqAttemptResponse:
    return pyq_service.evaluate(db, pyq_id, body.response_text)
