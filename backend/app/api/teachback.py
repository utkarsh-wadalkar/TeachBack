from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.teachback import (
    AttemptResponse,
    StartSessionRequest,
    StartSessionResponse,
    SubmitAttemptRequest,
    TranscribeResponse,
)
from app.services import teachback_service

router = APIRouter(prefix="/teachback", tags=["teachback"])


@router.post("/sessions", response_model=StartSessionResponse)
def start_session(
    body: StartSessionRequest, db: Session = Depends(get_db)
) -> StartSessionResponse:
    return teachback_service.start_session(db, body.concept_id)


@router.post("/sessions/{session_id}/attempts", response_model=AttemptResponse)
def submit_attempt(
    session_id: int, body: SubmitAttemptRequest, db: Session = Depends(get_db)
) -> AttemptResponse:
    return teachback_service.submit_attempt(
        db, session_id, body.response_text, body.modality
    )


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)) -> TranscribeResponse:
    audio = await file.read()
    text = teachback_service.transcribe_audio(
        audio, content_type=file.content_type or "audio/webm"
    )
    return TranscribeResponse(text=text)
