"""Schémas de requête/réponse de l'API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(default="", max_length=8000)
    code: str = Field(default="", max_length=60000)
    language: str = Field(default=None, pattern="^(python|c|javascript|java)$")
    exercise_slug: str | None = None
    student_id: int | None = None
    intro: bool = False  # demande explicite de la phase découverte (théorie + exemple)


class RunRequest(BaseModel):
    code: str = Field(max_length=60000)
    language: str = Field(pattern="^(python|c|javascript|java)$")
    exercise_slug: str | None = None
    student_id: int | None = None


class LanguageRequest(BaseModel):
    language: str = Field(pattern="^(python|c|javascript|java)$")
    student_id: int | None = None


class CreateStudentRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=60)
    language: str = Field(default="python", pattern="^(python|c|javascript|java)$")


class StartLevelRequest(BaseModel):
    student_id: int
    level: int = Field(ge=1, le=4)
