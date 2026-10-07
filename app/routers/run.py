from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import RunRequest
from ..services import student_state
from ..services.tutor import handle_run

router = APIRouter(prefix="/api", tags=["run"])


@router.post("/run")
def run(req: RunRequest) -> dict:
    student_id = req.student_id or student_state.ensure_student()
    try:
        return handle_run(
            student_id=student_id,
            language=req.language,
            code=req.code,
            exercise_slug=req.exercise_slug,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
