"""Raffinement LLM : classifie les chunks document restés sans concept
(detected_by=none) et met a jour concept/level/metadata en base.
Pas de re-embedding : le contenu ne change pas.
"""
import json
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.db import execute, fetch_all, get_pool  # noqa: E402
from app.services.curriculum import SKILLS  # noqa: E402
from app.services.qwen_client import qwen  # noqa: E402

sys.path.insert(0, str(BASE_DIR / "scripts"))
from ingest_documents import SKILLS_DESC  # noqa: E402

skill_levels = {s["slug"]: s["level"] for s in SKILLS}

rows = fetch_all(
    """
    SELECT id, title, content, language FROM kb_chunks
    WHERE metadata->>'kind' = 'document' AND metadata->>'detected_by' = 'none'
    ORDER BY id
    """
)
print(f"{len(rows)} chunks a classer par LLM")

system = (
    "Tu classifies des extraits de cours d'algorithmique.\n"
    f"Concepts possibles :\n{SKILLS_DESC}\n\n"
    'Réponds UNIQUEMENT en JSON : {"concept": "<slug ou null>", '
    '"level": <1-4 ou null>}.'
)

updated = 0
t0 = time.time()
for row in rows:
    user = (
        f"Titre de section : {row['title']}\n"
        f"Langage du document : {row['language']}\n\n"
        f"Contenu :\n{row['content'][:1200]}"
    )
    try:
        result = qwen.chat_json(system, user, temperature=0.0)
    except Exception as exc:
        print(f"  id={row['id']} echec LLM : {str(exc)[:80]}")
        continue
    concept = result.get("concept")
    level = result.get("level")
    if concept not in skill_levels:
        concept = None
    if level not in (1, 2, 3, 4):
        level = skill_levels.get(concept)
    metadata = {"kind": "document", "page": None, "detected_by": "llm"}
    execute(
        """
        UPDATE kb_chunks
        SET concept = COALESCE(%s, concept),
            level = COALESCE(%s, level),
            metadata = metadata || jsonb_build_object('detected_by', 'llm')
        WHERE id = %s
        """,
        (concept, level, row["id"]),
    )
    updated += 1
    print(f"  id={row['id']} [{concept or '-'} n{level or '-'}] {row['title'][:50]}")

print(f"{updated}/{len(rows)} chunks raffines en {round(time.time() - t0)}s")
get_pool().close()
print("REFINE_OK")
