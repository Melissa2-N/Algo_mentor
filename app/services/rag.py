"""Recherche hybride pgvector : distance cosinus (<=>) sur bge-m3 + filtres
de métadonnées (langage, niveau, concept).
"""
from __future__ import annotations

from ..db import fetch_all
from .embeddings import embed_query


def _vec_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{x:.7g}" for x in vector) + "]"


def search(
    query: str,
    language: str | None = None,
    concept: str | None = None,
    level: int | None = None,
    k: int = 4,
) -> list[dict]:
    """Recherche hybride : similarité cosinus + boost mot-clé sur le titre.

    1. Passe stricte : filtres métadonnées (langage exact, concept, niveau).
    2. Repli : filtre allégé (universal + langage) si trop peu de résultats.
    """
    vec = _vec_literal(embed_query(query))
    # Ordre des placeholders SQL : vec (SELECT), vec (WHERE seuil), filtres, like, k
    conditions, extra_params = ["1 - (embedding <=> %s::vector) > 0.2"], []

    if language:
        conditions.append("(metadata->>'language' = %s OR metadata->>'language' = 'universal')")
        extra_params.append(language)
    if concept:
        conditions.append("concept = %s")
        extra_params.append(concept)
    if level:
        conditions.append("level <= %s")
        extra_params.append(level)

    # boost hybride : les titres qui contiennent les mots de la requête gagnent
    like = "%" + query.strip().lower()[:40] + "%"
    sql = f"""
        SELECT id, concept, level, language, title, content, metadata,
               1 - (embedding <=> %s::vector)
                   + CASE WHEN lower(title) LIKE %s THEN 0.15 ELSE 0 END AS score
        FROM kb_chunks
        WHERE {' AND '.join(conditions)}
        ORDER BY score DESC
        LIMIT %s
    """
    # Ordre des placeholders SQL : vec (SELECT), like (SELECT), vec (WHERE seuil),
    # filtres, k — le CASE LIKE apparaît avant le WHERE dans la requête.
    rows = fetch_all(sql, tuple([vec, like, vec] + extra_params + [k]))

    if len(rows) < 2 and concept is None and language:
        # repli : relâche le filtre de langage
        return search(query, language=None, concept=concept, level=level, k=k)
    return rows
