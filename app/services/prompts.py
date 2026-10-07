"""Template de prompt strict appliquant la méthode socratique."""
from __future__ import annotations

SYSTEM_PROMPT = """Tu es un tuteur socratique d'algorithmique pour débutant complet.
RÈGLES ABSOLUES :
1. JAMAIS de code corrigé complet. Pas de solution brute.
2. Tu guides avec UN indice court (1 à 2 phrases) axé sur le concept manquant :
   une question socratique ou une analogie, jamais la ligne de code à écrire.
3. Tu t'exprimes en français, simplement, avec des images concrètes.
4. Tu t'appuies sur l'état de l'apprenant (compétences validées, erreurs
   récurrentes) pour personnaliser tes indices.
5. Tu t'appuies sur la trace d'erreur ou la sortie inattendue pour pointer la
   cause conceptuelle, sans la corriger toi-même.
6. La VALIDATION des compétences est gérée côté serveur : quand tous les
   tests passent, tu n'es pas appelé. Si la plupart des tests passent mais
   pas tous, félicite ce qui marche et concentre-toi sur ce qui échoue.
7. Les extraits RAG fournis sont la référence du langage choisi : n'en
   introduis pas d'un autre langage.
8. SITUATION : l'apprenant a DÉJÀ vu la théorie et un exemple de syntaxe
   générique (différent de la solution) lors de la phase découverte. Tu es
   en phase de PRATIQUE GUIDÉE : ne répète PAS l'exemple ni la théorie
   longue, analyse sa tentative et donne l'indice qui débloque.

Réponds UNIQUEMENT avec un objet JSON valide :
{
  "verdict": "blocked" | "partial" | "success",
  "theory": "rappel ULTRA court du concept (1 phrase maximum, optionnel)",
  "hint": "l'indice socratique (1-2 phrases, jamais de code corrigé)",
  "observation": "ce que tu as observé dans la sortie/trace (1-2 phrases)",
  "next_step": "l'action concrète suivante de l'apprenant (1 phrase)"
}
"""

JSON_EXAMPLE = """Exemple de réponse attendue (verdict "blocked") :
{"verdict": "blocked", "theory": "Une boucle while tourne tant que sa condition est vraie.", "hint": "Que devient ta variable i après chaque tour ? Est-ce qu'elle change ?", "observation": "Le programme ne se termine pas : aucun affichage, timeout après 3s.", "next_step": "Ajoute la progression vers la condition d'arrêt dans le corps de la boucle."}"""


# ---------------------------------------------------------------------------
# Mode questions/réponses libres (phase découverte, pratique, ou attente de
# confirmation) : l'apprenant pose une question sans soumettre de code.
# ---------------------------------------------------------------------------
QA_SYSTEM_PROMPT = """Tu es un tuteur socratique d'algorithmique pour débutant complet.
L'apprenant t'envoie un message libre : soit une question sur le cours (concept,
syntaxe, énoncé, notion qu'il ne comprend pas), soit une demande d'aide sur son
code, soit (rarement) une confirmation qu'il veut continuer.

CHOISIS LE MODE DE RÉPONSE selon la nature du message :

MODE "explanation" — l'apprenant pose une VRAIE question, en particulier sur un
concept QU'IL DÉCOUVRE (jamais vu ou mal compris) :
1. Explique vraiment : ce que c'est, à quoi ça sert, quand on l'utilise.
2. Donne la syntaxe GÉNÉRALE à retenir dans le langage choisi, avec un
   mini-exemple complet et GÉNÉRIQUE, différent de la solution de l'exercice.
3. Termine par une phrase qui relie au sujet en cours SANS donner la solution.
4. Vise 4 à 8 phrases courtes, vocabulaire débutant, analogie concrète
   bienvenue. Une vraie question mérite une vraie explication : NE TE LIMITE
   PAS à un indice de 1-2 phrases dans ce mode.

MODE "hint" — l'apprenant demande de l'aide sur son CODE QUI ÉCHOUe sur un
concept DÉJÀ enseigné (tests ou erreur fournis dans le contexte) :
1. Analyse l'observation/erreur fournie et donne un indice socratique de 1-2
   phrases centré sur le concept manquant.
2. JAMAIS de code corrigé complet, jamais la solution de l'exercice.

RÈGLES ABSOLUES (dans les deux modes) :
- Jamais la solution de l'exercice en cours, ni le code exact à recopier pour
  le réussir. Exemple générique obligatoirement différent de la solution.
- Appuie-toi sur les extraits RAG fournis (référence du langage choisi) et
  l'historique récent ; n'invente pas de syntaxe d'un autre langage.
- Si la question sort du sujet, réponds brièvement puis ramène au concept en cours.
- Si l'apprenant dit simplement qu'il n'a pas de question et veut continuer
  ("non", "ok", "c'est bon", "continue"...) : intent = "confirmation".

Réponds UNIQUEMENT avec un objet JSON valide :
{
  "intent": "question" | "confirmation",
  "mode": "explanation" | "hint",
  "answer": "ta réponse, formatée selon le mode choisi"
}"""

CONFIRMATION_QUESTION = (
    "Avant de valider cette compétence et de débloquer la suivante : "
    "as-tu des questions sur ce qu'on vient de voir, ou on continue ?"
)


def build_qa_message(
    *,
    student_name: str,
    language: str,
    skill: dict | None,
    exercise: dict | None,
    rag_chunks: list[dict],
    student_message: str,
    code: str,
    history: list[dict],
    stage: str,
    attempts: int = 0,
    test_results: list[dict] | None = None,
    run_output: dict | None = None,
) -> str:
    parts: list[str] = []
    phase = {
        "discovery": "découverte (théorie + exemple de syntaxe générique viennent d'être montrés, l'apprenant n'a pas encore codé)",
        "practicing": "pratique guidée (l'apprenant a déjà soumis des tentatives)",
        "awaiting_confirmation": "attente de confirmation : TOUS les tests de l'exercice viennent de passer, l'apprenant peut valider et continuer, ou poser une question",
    }.get(stage, stage)
    parts.append(
        f"## Apprenant\nNom : {student_name} | Langage choisi : {language}\n\n"
        f"## Phase pédagogique\n{phase} (tentatives déjà soumises : {attempts})"
    )
    if skill:
        parts.append(
            f"## Compétence en cours\n{skill['title']} (niveau {skill['level']}) :\n"
            f"{skill['theory']}"
        )
    if exercise:
        parts.append(
            f"## Exercice en cours (NE PAS donner sa solution)\n{exercise['title']}\n"
            f"{exercise['instructions']}"
        )
    if rag_chunks:
        refs = "\n\n".join(f"[{c['title']}]\n{c['content'][:800]}" for c in rag_chunks)
        parts.append(f"## Extraits de la base de connaissances (RAG)\n{refs}")
    if test_results:
        lines = []
        for t in test_results:
            line = f"- {'PASS' if t['passed'] else 'FAIL'} : {t['label']}"
            if not t["passed"]:
                line += f" | attendu : {t.get('expected')} / obtenu : {t.get('actual')}"
            lines.append(line)
        parts.append("## Résultats des tests (exécutés en sandbox)\n" + "\n".join(lines))
    if run_output:
        parts.append(
            "## Dernière exécution (sans tests)\n"
            f"exit={run_output.get('exit_code')} timed_out={run_output.get('timed_out')}\n"
            f"stdout :\n{(run_output.get('stdout') or '')[:500]}\n"
            f"stderr :\n{(run_output.get('stderr') or '')[:500]}"
        )
    if code.strip():
        parts.append(f"## Code actuel de l'apprenant ({language})\n```\n{code[:4000]}\n```")
    if history:
        hist = "\n".join(f"[{h['role']}] {h['content'][:400]}" for h in history)
        parts.append(f"## Historique récent\n{hist}")
    parts.append(f"## Message de l'apprenant\n{student_message}")
    parts.append(
        'Réponds en JSON : {"intent": "question"|"confirmation", '
        '"mode": "explanation"|"hint", "answer": "..."}'
    )
    return "\n\n".join(parts)


def build_user_message(
    *,
    student_name: str,
    language: str,
    skill: dict | None,
    validated: list[str],
    fragile: dict,
    exercise: dict | None,
    test_results: list[dict] | None,
    run_output: dict | None,
    rag_chunks: list[dict],
    student_message: str,
    code: str,
    history: list[dict],
    attempts: int = 0,
) -> str:
    parts: list[str] = []

    parts.append(f"## Apprenant\nNom : {student_name} | Langage choisi : {language}")
    parts.append(
        f"## Situation pédagogique\nPhase : pratique guidée (théorie + exemple de syntaxe "
        f"générique déjà montrés en découverte). Tentatives déjà soumises : {attempts}."
    )

    if skill:
        parts.append(
            f"## Compétence en cours\n{skill['title']} (niveau {skill['level']}) :\n"
            f"{skill['theory']}"
        )
    if validated:
        parts.append("## Compétences déjà validées\n" + ", ".join(validated))
    if fragile.get("by_kind"):
        kinds = ", ".join(f"{r['error_kind']} (x{r['occurrences']})" for r in fragile["by_kind"])
        parts.append(f"## Erreurs récurrentes de cet apprenant\n{kinds}")
    if fragile.get("by_skill"):
        skills = ", ".join(f"{r['skill_slug']}/{r['error_kind']}" for r in fragile["by_skill"])
        parts.append(f"## Erreurs récurrentes par compétence\n{skills}")

    if exercise:
        tests_desc = "\n".join(
            f"- {t['label']} : entrée [{t['stdin']}] -> attendu [{t['expected']}] "
            f"-> obtenu [{t['actual']}] {'PASS' if t['passed'] else 'FAIL'}"
            + (f" | stderr: {t['stderr'][:300]}" if t.get("stderr") and not t["passed"] else "")
            for t in (test_results or [])
        )
        parts.append(
            f"## Exercice\n{exercise['title']}\n{exercise['instructions']}\n\n"
            f"### Résultats des tests (sandbox exécutée)\n{tests_desc or 'non exécuté'}"
        )
    elif run_output:
        parts.append(
            "## Exécution sandbox (sans tests)\n"
            f"exit={run_output.get('exit_code')} timed_out={run_output.get('timed_out')}\n"
            f"stdout:\n{run_output.get('stdout', '')[:1500]}\n"
            f"stderr:\n{run_output.get('stderr', '')[:1500]}"
        )

    if rag_chunks:
        refs = "\n\n".join(
            f"[{c['title']}]\n{c['content'][:800]}" for c in rag_chunks
        )
        parts.append(f"## Extraits de la base de connaissances (RAG)\n{refs}")

    if code.strip():
        parts.append(f"## Code de l'apprenant ({language})\n```\n{code[:6000]}\n```")
    else:
        parts.append("## Code de l'apprenant\n(vide — il n'a pas encore écrit de code)")

    if history:
        hist = "\n".join(f"[{h['role']}] {h['content'][:400]}" for h in history)
        parts.append(f"## Historique récent\n{hist}")

    parts.append(f"## Message de l'apprenant\n{student_message or '(aucun texte, juste du code)'}")
    parts.append(JSON_EXAMPLE)
    return "\n\n".join(parts)
