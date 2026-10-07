from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import ChatRequest
from ..services import student_state
from ..services.test_specs import EXERCISES
from ..services.tutor import handle_chat

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
def chat(req: ChatRequest) -> dict:
    try:
        student_id = req.student_id or student_state.ensure_student()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Base de donnees indisponible : {exc}")
    try:
        return handle_chat(
            student_id=student_id,
            message=req.message,
            language=req.language,
            code=req.code,
            exercise_slug=req.exercise_slug,
            intro=req.intro,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/exercises")
def list_exercises() -> dict:
    return {
        "exercises": [
            {"slug": e.slug, "title": e.title, "instructions": e.instructions}
            for e in EXERCISES.values()
        ]
    }
