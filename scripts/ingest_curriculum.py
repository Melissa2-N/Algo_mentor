"""Ingestion du curriculum dans pgvector.

Genere curriculum/knowledge_base.jsonl (theorie universelle + exemples par
langage), calcule les embeddings bge-m3 (1024d) et remplit kb_chunks.

Usage : python scripts/ingest_curriculum.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.db import execute  # noqa: E402
from app.services import curriculum as cur  # noqa: E402
from app.services.embeddings import embed  # noqa: E402

JSONL_PATH = BASE_DIR / "curriculum" / "knowledge_base.jsonl"


def build_chunks() -> list[dict]:
    chunks: list[dict] = []
    for skill in cur.SKILLS:
        # Theorie universelle (independante du langage)
        chunks.append({
            "concept": skill["slug"],
            "level": skill["level"],
            "language": "universal",
            "title": f"{skill['title']} — theorie",
            "content": skill["theory"],
            "metadata": {"kind": "theory", "concept": skill["slug"], "level": skill["level"],
                         "language": "universal"},
        })
        # Exemple de syntaxe par langage
        for lang, code in cur.EXAMPLES.get(skill["slug"], {}).items():
            chunks.append({
                "concept": skill["slug"],
                "level": skill["level"],
                "language": lang,
                "title": f"{skill['title']} — exemple {cur.LANGUAGE_LABELS[lang]}",
                "content": code,
                "metadata": {
                    "kind": "example",
                    "concept": skill["slug"],
                    "level": skill["level"],
                    "language": lang,
                },
            })
    return chunks


def main() -> None:
    chunks = build_chunks()
    print(f"{len(chunks)} chunks construits — calcul des embeddings bge-m3...")
    vectors = embed([c["title"] + "\n" + c["content"] for c in chunks])

    JSONL_PATH.parent.mkdir(exist_ok=True)
    with JSONL_PATH.open("w", encoding="utf-8") as f:
        for chunk, vec in zip(chunks, vectors):
            chunk["embedding"] = vec
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"JSONL ecrit : {JSONL_PATH}")

    execute("DELETE FROM kb_chunks")
    execute("ALTER SEQUENCE kb_chunks_id_seq RESTART WITH 1")
    for chunk, vec in zip(chunks, vectors):
        execute(
            """
            INSERT INTO kb_chunks (concept, level, language, title, content, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s::vector)
            """,
            (
                chunk["concept"], chunk["level"], chunk["language"],
                chunk["title"], chunk["content"],
                json.dumps(chunk["metadata"]), "[" + ",".join(f"{x:.7g}" for x in vec) + "]",
            ),
        )
    print(f"{len(chunks)} chunks inseres dans kb_chunks.")


if __name__ == "__main__":
    main()
