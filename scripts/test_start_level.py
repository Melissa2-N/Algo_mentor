"""E2E : niveau de départ (auto-déclaration) + retour en arrière avec upgrade.

Parcours vérifié :
 1. POST /api/student/start-level niveau 3 -> niveaux 1-2 auto_declared,
    prochaine étape = première compétence du niveau 3 (binary_search)
 2. Idempotence du start-level
 3. Retour en arrière sur 'variables' (auto_declared) : découverte -> code
    correct -> awaiting_confirmation -> confirmation -> statut upgrade
    auto_declared -> validated_by_test, autres validations conservées
 4. /api/run sur une compétence auto_declared -> attente de confirmation
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0


def call(method: str, path: str, body: dict | None = None,
         timeout: int = 120) -> tuple[int, dict]:
    req = urllib.request.Request(
        BASE + path, method=method,
        headers={"Content-Type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
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


def tree_by_slug(prof: dict) -> dict:
    return {s["slug"]: s for s in prof["progress_tree"]}


def main() -> int:
    # Nettoyage : supprime les residus d'un run precedent interrompu
    # (echec silencieux si dernier profil restant : le refus 400 n'efface rien)
    status, listed = call("GET", "/api/students")
    for s in listed.get("students", []):
        if s["display_name"] == "TestLevel":
            call("DELETE", f"/api/students/{s['id']}")

    print("\n[1] Depart au niveau 3")
    status, created = call("POST", "/api/students",
                           {"display_name": "TestLevel", "language": "python"})
    check("POST /api/students -> 201", status == 201, str(created))
    sid = created["id"]

    status, res = call("POST", "/api/student/start-level",
                       {"student_id": sid, "level": 3})
    check("start-level -> 200", status == 200, str(res))
    prof = res["profile"]
    check("11 competences auto-declarees (7 niv.1 + 4 niv.2)",
          res["declared_count"] == 11, str(res.get("declared_count")))
    tree = tree_by_slug(prof)
    check("variables = auto_declared",
          tree["variables"]["validated"] and tree["variables"]["status"] == "auto_declared",
          str(tree["variables"]))
    check("stacks_queues = auto_declared",
          tree["stacks_queues"]["status"] == "auto_declared", str(tree["stacks_queues"]))
    check("binary_search non valide",
          not tree["binary_search"]["validated"], str(tree["binary_search"]))
    check("next_skill = binary_search (1re du niveau 3)",
          prof["next_skill"]["slug"] == "binary_search", str(prof["next_skill"]))

    print("\n[2] Idempotence")
    status, res2 = call("POST", "/api/student/start-level",
                        {"student_id": sid, "level": 3})
    check("second appel : 0 nouvelle declaration", res2["declared_count"] == 0,
          str(res2.get("declared_count")))

    print("\n[3] Retour en arriere sur 'variables' + upgrade")
    status, data = call("POST", "/api/chat", {
        "student_id": sid, "message": "", "code": "",
        "language": "python", "exercise_slug": "variables", "intro": True})
    check("intro retour arriere -> discovery", data["reply"]["verdict"] == "discovery",
          str(data["reply"])[:150])

    solution = 'prenom = "Alice"\nage = 15\nprint(f"Bonjour {prenom}, tu as {age} ans")'
    status, data = call("POST", "/api/chat", {
        "student_id": sid, "message": "", "code": solution,
        "language": "python", "exercise_slug": "variables"})
    check("tests passes", all(t["passed"] for t in (data["test_results"] or [])),
          str(data["test_results"]))
    check("verdict awaiting_confirmation", data["reply"]["verdict"] == "awaiting_confirmation",
          str(data["reply"])[:150])
    check("upgrade annonce", "déclaration" in data["reply"]["observation"],
          data["reply"]["observation"])

    status, data = call("POST", "/api/chat", {
        "student_id": sid, "message": "ok on continue",
        "code": "", "language": "python", "exercise_slug": "variables"})
    check("confirmation -> success", data["reply"]["verdict"] == "success",
          str(data["reply"])[:150])
    check("competence validee", data["skill_validated"])
    tree = tree_by_slug({"progress_tree": data["progress_tree"]})
    check("variables upgrade -> validated_by_test",
          tree["variables"]["status"] == "validated_by_test", str(tree["variables"]))
    check("types reste auto_declared", tree["types"]["status"] == "auto_declared",
          str(tree["types"]))
    check("next_skill toujours binary_search",
          data["profile"]["next_skill"]["slug"] == "binary_search",
          str(data["profile"]["next_skill"]))

    print("\n[4] /api/run sur une competence auto_declared")
    status, run = call("POST", "/api/run", {
        "student_id": sid, "language": "python",
        "code": "n = int(input())\nprint(n * 2)",
        "exercise_slug": "types"})
    check("run all_passed", run.get("all_passed"), str(run)[:200])
    check("stage awaiting_confirmation (upgradable)", run.get("stage") == "awaiting_confirmation",
          str(run))

    print("\n[5] Nettoyage")
    status, _ = call("DELETE", f"/api/students/{sid}")
    check("DELETE profil de test", status == 200)

    print(f"\n===== RESULTAT : {PASS} pass / {FAIL} fail =====")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
