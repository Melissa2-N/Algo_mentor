"""Suivi d'état de l'apprenant : compétences validées, notions fragiles,
progression (prochaine étape du cursus), historique de conversation.
"""
from __future__ import annotations

from ..db import execute, fetch_all, fetch_one
from .curriculum import SKILLS, SKILLS_BY_SLUG, next_skill


def ensure_student(display_name: str = "Apprenant", language: str = "python") -> int:
    """Profil par défaut si la base est vide (compatibilité)."""
    row = fetch_one("SELECT id FROM students ORDER BY id LIMIT 1")
    if row:
        return row["id"]
    return create_student(display_name, language)


# ---------------------------------------------------------------------------
# Profils multiples
# ---------------------------------------------------------------------------
def create_student(display_name: str, language: str = "python") -> int:
    row = fetch_one(
        "INSERT INTO students (display_name, language) VALUES (%s, %s) RETURNING id",
        (display_name.strip() or "Apprenant", language),
    )
    return row["id"]


def list_students() -> list[dict]:
    rows = fetch_all(
        """
        SELECT s.id, s.display_name, s.language, s.created_at,
               COUNT(sk.skill_slug) AS validated_count,
               COALESCE(MAX(sk.level_skill), 0) AS max_level
        FROM students s
        LEFT JOIN (
            SELECT student_id, skill_slug,
                   (SELECT level FROM skills WHERE slug = student_skills.skill_slug) AS level_skill
            FROM student_skills WHERE validated
        ) sk ON sk.student_id = s.id
        GROUP BY s.id
        ORDER BY s.id
        """
    )
    for r in rows:
        r["level"] = min(max(r.pop("max_level"), 0) + 1, 4)
    return rows


def delete_student(student_id: int) -> None:
    """Suppression en cascade (student_skills, error_events, chat_messages,
    student_stages). Refus du dernier profil restant."""
    count = fetch_one("SELECT COUNT(*) AS n FROM students")["n"]
    if count <= 1:
        raise ValueError("Impossible de supprimer le dernier profil restant.")
    execute("DELETE FROM students WHERE id = %s", (student_id,))


def set_language(student_id: int, language: str) -> None:
    execute("UPDATE students SET language = %s WHERE id = %s", (language, student_id))


def get_language(student_id: int) -> str:
    row = fetch_one("SELECT language FROM students WHERE id = %s", (student_id,))
    return row["language"] if row else "python"


def validated_skills(student_id: int) -> set[str]:
    rows = fetch_all(
        "SELECT skill_slug FROM student_skills WHERE student_id = %s AND validated",
        (student_id,),
    )
    return {r["skill_slug"] for r in rows}


def skill_status(student_id: int, skill_slug: str) -> str | None:
    """Statut d'acquisition : 'validated_by_test', 'auto_declared' ou None."""
    row = fetch_one(
        "SELECT status FROM student_skills "
        "WHERE student_id = %s AND skill_slug = %s AND validated",
        (student_id, skill_slug),
    )
    if row is None:
        return None
    return row["status"] or "validated_by_test"


def auto_declare_below(student_id: int, level: int) -> int:
    """Départ à un niveau N > 1 : toutes les compétences des niveaux < N sont
    marquées acquises avec le statut 'auto_declared' (sans toucher aux
    validations existantes). Retourne le nombre de compétences déclarées."""
    row = fetch_one(
        """
        WITH inserted AS (
            INSERT INTO student_skills (student_id, skill_slug, validated, validated_at, status, attempts)
            SELECT %s, s.slug, true, now(), 'auto_declared', 0
            FROM skills s
            WHERE s.level < %s
              AND NOT EXISTS (
                  SELECT 1 FROM student_skills sk
                  WHERE sk.student_id = %s AND sk.skill_slug = s.slug
              )
            RETURNING 1
        )
        SELECT COUNT(*) AS n FROM inserted
        """,
        (student_id, level, student_id),
    )
    return row["n"]


def get_attempts(student_id: int, skill_slug: str) -> int:
    """Nombre de tentatives déjà soumises pour une compétence (0 = premier contact)."""
    row = fetch_one(
        "SELECT attempts FROM student_skills WHERE student_id = %s AND skill_slug = %s",
        (student_id, skill_slug),
    )
    return row["attempts"] if row else 0


def record_attempt(student_id: int, skill_slug: str) -> None:
    execute(
        """
        INSERT INTO student_skills (student_id, skill_slug, attempts)
        VALUES (%s, %s, 1)
        ON CONFLICT (student_id, skill_slug)
        DO UPDATE SET attempts = student_skills.attempts + 1
        """,
        (student_id, skill_slug),
    )


def validate_skill(
    student_id: int, skill_slug: str, status: str = "validated_by_test"
) -> None:
    execute(
        """
        INSERT INTO student_skills (student_id, skill_slug, validated, validated_at, status, attempts)
        VALUES (%s, %s, true, now(), %s, 1)
        ON CONFLICT (student_id, skill_slug)
        DO UPDATE SET validated = true, validated_at = now(), status = EXCLUDED.status
        """,
        (student_id, skill_slug, status),
    )
    clear_stage(student_id, skill_slug)


# ---------------------------------------------------------------------------
# Étape courante de la boucle pédagogique (par compétence)
# ---------------------------------------------------------------------------
def get_stage(student_id: int, skill_slug: str) -> str:
    row = fetch_one(
        "SELECT stage FROM student_stages WHERE student_id = %s AND skill_slug = %s",
        (student_id, skill_slug),
    )
    return row["stage"] if row else "discovery"


def set_stage(student_id: int, skill_slug: str, stage: str) -> None:
    execute(
        """
        INSERT INTO student_stages (student_id, skill_slug, stage)
        VALUES (%s, %s, %s)
        ON CONFLICT (student_id, skill_slug)
        DO UPDATE SET stage = EXCLUDED.stage, updated_at = now()
        """,
        (student_id, skill_slug, stage),
    )


def clear_stage(student_id: int, skill_slug: str) -> None:
    execute(
        "DELETE FROM student_stages WHERE student_id = %s AND skill_slug = %s",
        (student_id, skill_slug),
    )


def record_error(student_id: int, skill_slug: str | None, error_kind: str, detail: str) -> None:
    execute(
        "INSERT INTO error_events (student_id, skill_slug, error_kind, detail) "
        "VALUES (%s, %s, %s, %s)",
        (student_id, skill_slug, error_kind, detail[:500]),
    )


def fragile_notions(student_id: int, min_occurrences: int = 2) -> list[dict]:
    """Erreurs récurrentes : comptées par type et par compétence."""
    by_kind = fetch_all(
        """
        SELECT error_kind, COUNT(*) AS occurrences,
               MAX(occurred_at) AS last_seen
        FROM error_events
        WHERE student_id = %s
        GROUP BY error_kind
        HAVING COUNT(*) >= %s
        ORDER BY occurrences DESC
        """,
        (student_id, min_occurrences),
    )
    by_skill = fetch_all(
        """
        SELECT skill_slug, error_kind, COUNT(*) AS occurrences
        FROM error_events
        WHERE student_id = %s AND skill_slug IS NOT NULL
        GROUP BY skill_slug, error_kind
        HAVING COUNT(*) >= %s
        ORDER BY occurrences DESC
        """,
        (student_id, min_occurrences),
    )
    return {"by_kind": by_kind, "by_skill": by_skill}


def current_level(student_id: int) -> int:
    """Niveau actuel : 1 + niveau max des compétences validées (borné à 4)."""
    validated = validated_skills(student_id)
    levels = [SKILLS_BY_SLUG[s]["level"] for s in validated if s in SKILLS_BY_SLUG]
    return min(max(levels, default=0) + 1, 4)


def get_profile(student_id: int) -> dict:
    row = fetch_one("SELECT * FROM students WHERE id = %s", (student_id,))
    if row is None:
        raise ValueError(f"student {student_id} introuvable")
    validated = validated_skills(student_id)
    statuses = {
        r["skill_slug"]: r["status"] or "validated_by_test"
        for r in fetch_all(
            "SELECT skill_slug, status FROM student_skills "
            "WHERE student_id = %s AND validated",
            (student_id,),
        )
    }
    nxt = next_skill(validated)
    return {
        "id": row["id"],
        "display_name": row["display_name"],
        "language": row["language"],
        "level": current_level(student_id),
        "validated_skills": [
            {
                "slug": slug,
                "title": SKILLS_BY_SLUG[slug]["title"],
                "level": SKILLS_BY_SLUG[slug]["level"],
                "status": statuses.get(slug, "validated_by_test"),
            }
            for slug in SKILLS_BY_SLUG
            if slug in validated
        ],
        "total_skills": len(SKILLS),
        "next_skill": nxt,
        "fragile": fragile_notions(student_id),
    }


def add_message(student_id: int, role: str, content: str) -> None:
    execute(
        "INSERT INTO chat_messages (student_id, role, content) VALUES (%s, %s, %s)",
        (student_id, role, content[:8000]),
    )


def get_history(student_id: int, limit: int = 8) -> list[dict]:
    rows = fetch_all(
        """
        SELECT role, content FROM chat_messages
        WHERE student_id = %s
        ORDER BY id DESC LIMIT %s
        """,
        (student_id, limit),
    )
    return list(reversed(rows))


def progress_tree(student_id: int) -> list[dict]:
    """Arbre du cursus avec l'état de chaque compétence pour l'UI."""
    validated = validated_skills(student_id)
    statuses = {
        r["skill_slug"]: r["status"] or "validated_by_test"
        for r in fetch_all(
            "SELECT skill_slug, status FROM student_skills "
            "WHERE student_id = %s AND validated",
            (student_id,),
        )
    }
    tree = []
    for skill in SKILLS:
        tree.append({
            "slug": skill["slug"],
            "title": skill["title"],
            "level": skill["level"],
            "validated": skill["slug"] in validated,
            "status": statuses.get(skill["slug"]),
            "unlocked": all(p in validated for p in skill["prerequisites"]),
        })
    return tree
