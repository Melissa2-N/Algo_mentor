from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import CreateStudentRequest, LanguageRequest, StartLevelRequest
from ..services import student_state
from ..services.curriculum import SKILLS

router = APIRouter(prefix="/api", tags=["student"])


@router.get("/student")
def get_profile(student_id: int | None = None) -> dict:
    try:
        sid = student_id or student_state.ensure_student()
        profile = student_state.get_profile(sid)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Base de donnees indisponible : {exc}")
    profile["progress_tree"] = student_state.progress_tree(sid)
    profile["skills_catalog"] = [
        {"slug": s["slug"], "title": s["title"], "level": s["level"],
         "prerequisites": s["prerequisites"]}
        for s in SKILLS
    ]
    return profile


# ---------------------------------------------------------------------------
# Gestion de plusieurs profils apprenant
# ---------------------------------------------------------------------------
@router.get("/students")
def list_students() -> dict:
    try:
        return {"students": student_state.list_students()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Base de donnees indisponible : {exc}")


@router.post("/students", status_code=201)
def create_student(req: CreateStudentRequest) -> dict:
    try:
        sid = student_state.create_student(req.display_name, req.language)
        return student_state.get_profile(sid)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Base de donnees indisponible : {exc}")


@router.delete("/students/{student_id}")
def delete_student(student_id: int) -> dict:
    try:
        student_state.delete_student(student_id)  # cascade : skills, erreurs, chat, stages
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Base de donnees indisponible : {exc}")
    return {"ok": True, "deleted": student_id}


@router.post("/student/language")
def set_language(req: LanguageRequest) -> dict:
    sid = req.student_id or student_state.ensure_student()
    student_state.set_language(sid, req.language)
    return {"ok": True, "language": req.language}


@router.post("/student/start-level")
def start_level(req: StartLevelRequest) -> dict:
    """Départ à un niveau N : les compétences des niveaux < N sont marquées
    'auto_declared' (distinct de 'validated_by_test'), et la prochaine étape
    devient la première compétence du niveau N."""
    try:
        declared = student_state.auto_declare_below(req.student_id, req.level)
        profile = student_state.get_profile(req.student_id)
        profile["progress_tree"] = student_state.progress_tree(req.student_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Base de donnees indisponible : {exc}")
    return {"declared_count": declared, "profile": profile}
