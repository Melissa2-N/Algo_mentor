"""Test RAG + chat (sans cle Qwen : verifie la degradation gracieuse)."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.db import get_pool  # noqa: E402
from app.services.rag import search  # noqa: E402

chunks = search("comment faire une boucle for qui compte", language="python", k=3)
print("RAG_TOP:", [(c["title"], round(c["score"], 3)) for c in chunks])
assert any(c["concept"] in ("for_loop", "while_loop") for c in chunks), "RAG should find loop chunks"

chunks2 = search("comment afficher une variable", language="python", concept="variables", k=2)
print("RAG_CONCEPT:", [(c["title"], round(c["score"], 3)) for c in chunks2])
assert chunks2 and all(c["concept"] == "variables" for c in chunks2)

from app.services import student_state  # noqa: E402
from app.services.tutor import handle_chat  # noqa: E402

sid = student_state.ensure_student()
result = handle_chat(
    student_id=sid, message="Je ne comprends pas comment afficher la somme",
    language="python",
    code="n = 10\nfor i in range(n):\n    total = total + i\nprint(total)",
    exercise_slug="for_loop",
)
print("VERDICT:", result["reply"]["verdict"])
print("HINT:", result["reply"]["hint"][:100])
print("TESTS:", [(t["label"], t["passed"]) for t in result["test_results"]])
print("RAG in context OK, chat OK")
get_pool().close()
print("RAG_CHAT_OK")
sys.exit(0)
