"""Test RAG final : requetes sur les documents PDF ingeres."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.db import get_pool  # noqa: E402
from app.services.rag import search  # noqa: E402

queries = [
    ("comment fonctionne une boucle tant que", "python"),
    ("la recursion c'est quoi", "universal"),
    ("printf et scanf en C", "c"),
    ("les methode recursives en java", "java"),
    ("try except en python", "python"),
    ("tri par selection", "universal"),
    ("l algorigramme", "universal"),
    ("la methode du pivot", "universal"),
    ("savoir ecrire un algorithme", "universal"),
    ("les objets en java", "java"),
]
for q, lang in queries:
    rows = search(q, language=lang, k=6)
    tops = [(r["metadata"].get("kind"), r["concept"], r["title"][:48], round(r["score"], 2))
            for r in rows]
    print(f"Q: {q!r}")
    for t in tops:
        print(f"   {t}")
    assert rows, f"aucun resultat pour {q!r}"

get_pool().close()
print("RAG_DOCS_OK")
