"""Test bout en bout : multi-profils + boucle conversationnelle.

Parcours verifie (via l'API HTTP, serveur lance au prealable) :
 1. Creation / listing / suppression de profils
 2. Decouverte (theorie + exemple) puis question libre en phase decouverte -> Q&A
 3. Code correct -> awaiting_confirmation (PAS de validation immediate)
 4. Question en attente de confirmation -> reponse, competence non validee
 5. Confirmation -> competence validee + decouverte de la suivante
 6. Refus de supprimer le dernier profil
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:8000"

PASS = 0
FAIL = 0


def call(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    req = urllib.request.Request(
        BASE + path,
        method=method,
        headers={"Content-Type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode() or "{}")


def check(label: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label} {extra}")


def chat(student_id: int, message: str = "", code: str = "",
         exercise_slug: str | None = None, intro: bool = False) -> dict:
    status, data = call("POST", "/api/chat", {
        "student_id": student_id, "message": message, "code": code,
        "exercise_slug": exercise_slug, "intro": intro,
    })
    assert status == 200, f"chat HTTP {status}: {data}"
    return data


def main() -> int:
    # ---------- 1. Profils ----------
    print("\n[1] Gestion des profils")
    status, created = call("POST", "/api/students",
                           {"display_name": "TestConv", "language": "python"})
    check("POST /api/students -> 201", status == 201, str(created))
    sid = created["id"]
    status, listed = call("GET", "/api/students")
    names = [s["display_name"] for s in listed["students"]]
    check("GET /api/students contient le nouveau profil", "TestConv" in names, str(names))
    status, listed = call("GET", "/api/students")
    mine = [s for s in listed["students"] if s["id"] == sid][0]
    check("nouveau profil a validated_count=0, level=1",
          mine["validated_count"] == 0 and mine["level"] == 1, str(mine))

    # ---------- 2. Decouverte + Q&A en phase decouverte ----------
    print("\n[2] Decouverte puis question libre")
    data = chat(sid, intro=True, exercise_slug="variables")
    check("intro -> verdict discovery", data["reply"]["verdict"] == "discovery",
          str(data["reply"])[:200])
    check("discovery a theorie + exemple + probleme",
          bool(data["reply"]["theory"]) and bool(data["reply"]["example"])
          and bool(data["reply"]["problem"]))

    data = chat(sid, message="C'est quoi exactement une variable ?",
                exercise_slug="variables")
    check("question libre -> verdict qa", data["reply"]["verdict"] == "qa",
          str(data["reply"])[:200])
    check("reponse qa non vide", bool(data["reply"].get("answer")))
    check("pas valide apres une question", not data["skill_validated"])

    # Reproduction du bug signale : question posee ALORS QUE l'editeur contient
    # du code -> doit passer en Q&A explicatif, pas en indice socratique cryptique
    print("\n[2 bis] Question AVEC code dans l'editeur (bug corrige)")
    data = chat(
        sid,
        message="ya pas autre methode pour le faire ? c'est quoi une f-string "
                "et pourquoi on l'utilise ?",
        code='prenom = Alice\nprint("Bonjour " + prenom)',
        exercise_slug="variables",
    )
    check("question AVEC code -> verdict qa", data["reply"]["verdict"] == "qa",
          str(data["reply"])[:200])
    check("reponse explicative substantielle (pas un simple indice)",
          len(data["reply"].get("answer", "")) >= 80,
          str(data["reply"].get("answer", ""))[:120])
    check("toujours pas valide", not data["skill_validated"])

    # ---------- 3. Code correct -> awaiting_confirmation ----------
    print("\n[3] Code correct -> attente de confirmation")
    solution = 'prenom = "Alice"\nage = 15\nprint(f"Bonjour {prenom}, tu as {age} ans")'
    data = chat(sid, code=solution, exercise_slug="variables")
    check("tests tous passes", all(t["passed"] for t in (data["test_results"] or [])),
          str(data["test_results"]))
    check("verdict awaiting_confirmation", data["reply"]["verdict"] == "awaiting_confirmation",
          str(data["reply"])[:200])
    check("PAS valide immediatement", not data["skill_validated"])
    check("stage = awaiting_confirmation", data["stage"] == "awaiting_confirmation",
          str(data.get("stage")))

    # le bouton Exécuter ne valide pas non plus
    status, run = call("POST", "/api/run", {
        "student_id": sid, "language": "python",
        "code": solution, "exercise_slug": "variables"})
    check("/api/run : all_passed sans validation", run["all_passed"] and run.get("stage")
          == "awaiting_confirmation", str(run)[:200])

    # ---------- 4. Question en attente de confirmation ----------
    print("\n[4] Question pendant l'attente de confirmation")
    data = chat(sid, message="Pourquoi on utilise des guillemets autour d'Alice ?",
                exercise_slug="variables")
    check("verdict qa", data["reply"]["verdict"] == "qa", str(data["reply"])[:200])
    check("toujours pas valide", not data["skill_validated"])
    check("stage toujours awaiting_confirmation", data["stage"] == "awaiting_confirmation",
          str(data.get("stage")))

    # ---------- 5. Confirmation -> validation + decouverte suivante ----------
    print("\n[5] Confirmation puis deblocage")
    data = chat(sid, message="non c'est bon, on peut continuer", exercise_slug="variables")
    check("verdict success", data["reply"]["verdict"] == "success", str(data["reply"])[:200])
    check("competence validee", data["skill_validated"])
    check("decouverte de la suivante incluse (theorie + exemple)",
          bool(data["reply"].get("theory")) and bool(data["reply"].get("example")),
          str(data["reply"])[:200])
    prof = data["profile"]
    check("variables dans les competences validees",
          any(v["slug"] == "variables" for v in prof["validated_skills"]))
    check("next_skill = types", prof["next_skill"]["slug"] == "types",
          str(prof["next_skill"]))

    # ---------- 6. Suppression ----------
    print("\n[6] Suppression de profils")
    status, _ = call("DELETE", f"/api/students/{sid}")
    check("DELETE profil -> 200", status == 200)
    status, listed = call("GET", "/api/students")
    check("profil disparu de la liste",
          all(s["id"] != sid for s in listed["students"]))
    # refus de supprimer le dernier : on ne tente la suppression que s'il ne
    # reste EXACTEMENT qu'un profil (le refus 400 n'efface rien) ; sinon on
    # saute ce check pour ne jamais risquer un profil reel.
    status, listed = call("GET", "/api/students")
    if len(listed["students"]) == 1:
        last_id = listed["students"][0]["id"]
        status, err = call("DELETE", f"/api/students/{last_id}")
        check("DELETE dernier profil -> 400", status == 400, str(err))
    else:
        check("DELETE dernier profil -> saute (autres profils presents)", True)

    print(f"\n===== RESULTAT : {PASS} pass / {FAIL} fail =====")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
