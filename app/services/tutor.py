"""Boucle pédagogique : orchestration complète d'un tour de tutorat.

1. Réception code + message + langage
2. Exécution sandbox (+ tests si exercice) ; classification des erreurs
3. Recherche RAG dans la base de connaissances
4. Construction du prompt socratique -> Qwen
5. Mise à jour de l'état apprenant (validation / erreurs récurrentes)
"""
from __future__ import annotations

import re
from dataclasses import asdict

from ..sandbox.runner import run_code, run_tests
from . import student_state
from .curriculum import LANGUAGE_LABELS, SKILLS_BY_SLUG
from .discovery_examples import DISCOVERY_EXAMPLES
from .prompts import (
    CONFIRMATION_QUESTION,
    QA_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_qa_message,
    build_user_message,
)
from .qwen_client import qwen
from .rag import search
from .test_specs import get_exercise


# Mots-clés de confirmation (repli si le LLM est indisponible)
_CONFIRM_RE = re.compile(
    r"^\s*(non|ok|okay|d'?accord|c'?est bon|ça marche|ca marche|continue|"
    r"continuer|go|next|suivant|suite|on continue|pas de question|aucune|"
    r"aucune question|rien|non merci|nope|nop|j'?ai compris|valide|"
    r"valider|passe|passer)\b",
    re.IGNORECASE,
)


def _is_confirmation(message: str) -> bool:
    """Repli par mots-clés : détecte 'je n'ai pas de question, continue'."""
    return bool(_CONFIRM_RE.match(message.strip()))


# ---------------------------------------------------------------------------
# Classification des erreurs (notions fragiles)
# ---------------------------------------------------------------------------
def classify_error(stderr: str, timed_out: bool, language: str) -> tuple[str, str]:
    if timed_out:
        return "infinite_loop", "Execution interrompue : boucle infinie probable"
    low = stderr.lower()
    if "segmentation fault" in low:
        return "segfault", stderr[:300]
    if "indexerror" in low or "out of bounds" in low or "index out of range" in low:
        return "index_error", stderr[:300]
    if "arrayindexoutofbounds" in low:
        return "index_error", stderr[:300]
    if "typeerror" in low or "incompatible types" in low or "lvalue" in low:
        return "type_error", stderr[:300]
    if "syntaxerror" in low or "syntax error" in low or "expected" in low and language == "c":
        return "syntax_error", stderr[:300]
    if "nameerror" in low or "undefined reference" in low or "cannot find symbol" in low:
        return "name_error", stderr[:300]
    if "compilation" in low or "error:" in low and language in ("c", "java"):
        return "compile_error", stderr[:300]
    if "valueerror" in low or "numberformatexception" in low or "nan" in low:
        return "conversion_error", stderr[:300]
    if low:
        return "runtime_error", stderr[:300]
    return "other", stderr[:300]


def _chunk_for_context(chunk: dict) -> dict:
    return {
        "title": chunk["title"],
        "content": chunk["content"],
        "language": chunk["language"],
        "concept": chunk["concept"],
    }


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------
def _discovery_reply(skill: dict, exercise, lang: str) -> dict:
    """Premier contact avec une compétence : théorie + exemple de syntaxe
    générique (différent de la solution) + énoncé du problème. Aucun indice
    socratique à ce stade : l'apprenant n'a encore rien tenté."""
    example = DISCOVERY_EXAMPLES.get(skill["slug"], {}).get(lang, "")
    return {
        "verdict": "discovery",
        "theory": skill["theory"],
        "example": example,
        "problem": exercise.instructions if exercise else skill["description"],
        "hint": "",
        "observation": "",
        "next_step": (
            "Observe bien l'exemple ci-dessus, puis écris ton propre code dans "
            "l'éditeur et clique sur Exécuter. Si tu bloques, demande-moi de l'aide."
        ),
    }


def _rag(query: str, lang: str, skill: dict | None, k: int = 3) -> list[dict]:
    try:
        return search(
            query,
            language=lang,
            concept=skill["slug"] if skill else None,
            level=skill["level"] if skill else None,
            k=k,
        )
    except Exception as exc:  # RAG indisponible : on degrade sans bloquer
        print(f"[tutor] RAG indisponible : {exc}")
        return []


def _handle_free_message(
    *,
    student_id: int,
    message: str,
    lang: str,
    skill: dict | None,
    skill_slug: str | None,
    exercise,
    stage: str,
    already_validated: bool,
    skill_status: str | None = None,
    attempts: int,
    code: str,
    payload,
    test_results: list[dict] | None = None,
    run_output: dict | None = None,
) -> dict:
    """Message écrit (avec ou sans code) : vraie question sur le concept ->
    explication complète ; demande d'aide sur du code qui échoue -> indice
    socratique court ; confirmation quand les tests viennent de passer."""
    profile = student_state.get_profile(student_id)
    rag_chunks = _rag(message, lang, skill)

    answer = ""
    intent: str | None = None
    if qwen.configured:
        user_message = build_qa_message(
            student_name=profile["display_name"],
            language=LANGUAGE_LABELS.get(lang, lang),
            skill=skill,
            exercise={"title": exercise.title, "instructions": exercise.instructions}
            if exercise else None,
            rag_chunks=[_chunk_for_context(c) for c in rag_chunks],
            student_message=message,
            code=code,
            history=student_state.get_history(student_id),
            stage=stage,
            attempts=attempts,
            test_results=test_results,
            run_output=run_output,
        )
        try:
            raw = qwen.chat_json(QA_SYSTEM_PROMPT, user_message)
            intent = raw.get("intent", "question")
            answer = (raw.get("answer") or "").strip()
        except Exception as exc:
            print(f"[tutor] Erreur API Qwen (QA) : {exc}")
    if intent is None:
        # LLM indisponible ou en erreur : repli mots-clés pour la confirmation
        if stage == "awaiting_confirmation" and _is_confirmation(message):
            intent = "confirmation"
        else:
            intent = "question"
            answer = (
                "Le modele est momentanement indisponible, reessaie dans un instant. "
                "En attendant, relis l'exemple de syntaxe montre lors de la decouverte."
            )

    # --- Confirmation : tests deja passés, l'apprenant n'a pas de question.
    # Valide une compétence nouvelle, ou UPGRADE une auto_declared vers
    # validated_by_test (retour en arrière retravaillé avec succès).
    upgradable = (not already_validated) or skill_status == "auto_declared"
    if stage == "awaiting_confirmation" and intent == "confirmation" and upgradable and skill_slug:
        was_declared = skill_status == "auto_declared"
        student_state.validate_skill(student_id, skill_slug)  # -> validated_by_test
        new_profile = student_state.get_profile(student_id)
        nxt = new_profile["next_skill"]
        next_skill = SKILLS_BY_SLUG.get(nxt["slug"]) if nxt else None
        next_exercise = get_exercise(nxt["slug"]) if nxt else None
        title = skill["title"] if skill else skill_slug
        reply = {
            "verdict": "success",
            "observation": (
                f"Parfait ! « {title} » passe d'acquis par déclaration à "
                "validé par test : c'est maintenant confirmé par la pratique."
                if was_declared
                else f"Parfait ! Competence « {title} » validee."
            ),
            "hint": "",
        }
        exercise_info = None
        if next_skill:
            disc = _discovery_reply(next_skill, next_exercise, lang)
            reply.update({
                "theory": disc["theory"],
                "example": disc["example"],
                "problem": disc["problem"],
                "next_step": disc["next_step"],
            })
            exercise_info = (
                {"slug": next_exercise.slug, "title": next_exercise.title,
                 "instructions": next_exercise.instructions}
                if next_exercise else None
            )
        else:
            reply.update({
                "theory": "", "example": "", "problem": "",
                "next_step": "Cursus termine — felicitations !",
            })
        student_state.add_message(student_id, "user", message)
        student_state.add_message(
            student_id, "tutor",
            f"[success] {reply['observation']} Competence suivante : "
            f"{next_skill['title'] if next_skill else 'cursus termine'}."
        )
        return payload(reply, skill_validated=True, exercise_info=exercise_info)

    # --- Question classique : on repond, l'etape ne change pas
    reply = {
        "verdict": "qa",
        "answer": answer,
        "observation": "",
        "hint": "",
        "theory": "",
        "example": "",
        "problem": "",
    }
    if stage == "awaiting_confirmation":
        # on re-pose la question de confirmation apres la reponse
        reply["next_step"] = CONFIRMATION_QUESTION
    elif stage == "discovery":
        reply["next_step"] = (
            "Quand tu te sens pret, ecris ton code dans l'editeur et teste-le."
        )
    else:
        reply["next_step"] = (
            "Continue ton code, puis teste-le ou demande-moi un indice."
        )
    student_state.add_message(student_id, "user", message)
    student_state.add_message(
        student_id, "tutor", f"[qa] {reply['answer']} {reply['next_step']}"
    )
    return payload(reply)


def handle_chat(
    *,
    student_id: int,
    message: str,
    language: str | None,
    code: str = "",
    exercise_slug: str | None = None,
    intro: bool = False,
) -> dict:
    lang = language or student_state.get_language(student_id)
    if language and language != student_state.get_language(student_id):
        student_state.set_language(student_id, lang)

    validated = sorted(student_state.validated_skills(student_id))

    # --- 1. Exercice cible : l'exercice demande, ou la prochaine etape du cursus
    exercise = get_exercise(exercise_slug) if exercise_slug else None
    skill_slug = exercise.slug if exercise else None
    if exercise is None:
        nxt = student_state.get_profile(student_id)["next_skill"]
        skill_slug = nxt["slug"] if nxt else None
        exercise = get_exercise(skill_slug) if skill_slug else None
    skill = SKILLS_BY_SLUG.get(skill_slug) if skill_slug else None

    attempts = student_state.get_attempts(student_id, skill_slug) if skill_slug else 0
    already_validated = skill_slug in validated if skill_slug else False
    status = (
        student_state.skill_status(student_id, skill_slug) if skill_slug else None
    )
    stage = student_state.get_stage(student_id, skill_slug) if skill_slug else "practicing"

    def payload(reply, *, test_results=None, run_output=None,
                skill_validated=False, exercise_info=None):
        return {
            "reply": reply,
            "skill_validated": skill_validated,
            "stage": student_state.get_stage(student_id, skill_slug)
            if skill_slug else None,
            "exercise": exercise_info or (
                {"slug": exercise.slug, "title": exercise.title,
                 "instructions": exercise.instructions}
                if exercise else None
            ),
            "test_results": test_results,
            "run_output": run_output,
            "profile": student_state.get_profile(student_id),
            "progress_tree": student_state.progress_tree(student_id),
        }

    # --- 2. Phase découverte : demandée explicitement, ou tout premier contact
    # (théorie + exemple de syntaxe générique, PAS d'appel LLM, PAS d'indice)
    if skill and (
        intro
        or (not code.strip() and not message.strip() and attempts == 0
            and not already_validated)
    ):
        if not already_validated:
            student_state.set_stage(student_id, skill_slug, "discovery")
        reply = _discovery_reply(skill, exercise, lang)
        student_state.add_message(
            student_id, "user", message or f"(découverte : {skill_slug})"
        )
        student_state.add_message(
            student_id, "tutor",
            f"[discovery] {skill['title']} : théorie + exemple montrés."
        )
        return payload(reply)

    # --- 3. Code soumis : exécution sandbox + tests (toujours, pour tracer
    # les tentatives et nourrir le contexte, même quand un message accompagne)
    test_results: list[dict] | None = None
    run_output: dict | None = None
    all_passed = False
    if code.strip():
        if exercise:
            student_state.record_attempt(student_id, exercise.slug)
            attempts += 1
            test_results = run_tests(lang, code, exercise.tests)
            all_passed = bool(test_results) and all(t["passed"] for t in test_results)
        else:
            run = run_code(lang, code)
            run_output = asdict(run)
            if not run.ok:
                kind, detail = classify_error(run.stderr, run.timed_out, lang)
                student_state.record_error(student_id, skill_slug, kind, detail)

    if exercise and code.strip() and not all_passed:
        # tentative échouée -> pratique guidée (indices socratiques)
        student_state.set_stage(student_id, skill_slug, "practicing")
        stage = "practicing"

    # --- 4. Message écrit = question / demande d'aide -> mode Q&A, MÊME quand
    # du code est présent (le LLM choisit explication ou indice selon le cas).
    # Exception : tous les tests passent -> on passe en attente de confirmation.
    if message.strip() and not (all_passed and exercise):
        return _handle_free_message(
            student_id=student_id, message=message, lang=lang,
            skill=skill, skill_slug=skill_slug, exercise=exercise,
            stage=stage, already_validated=already_validated,
            skill_status=status, attempts=attempts, code=code, payload=payload,
            test_results=test_results, run_output=run_output,
        )

    # --- 5. Transition d'état selon le résultat des tests
    if all_passed and exercise:
        if already_validated and status == "validated_by_test":
            # Retour en arrière sur une compétence déjà validée par test :
            # simple entraînement, rien ne change.
            reply = {
                "verdict": "success",
                "theory": "", "example": "", "problem": "", "hint": "",
                "observation": "Tous les tests passent toujours : cette compétence est déjà validée par test.",
                "next_step": "Tu peux passer à la compétence suivante ou t'entraîner davantage.",
            }
            student_state.add_message(student_id, "user", message or "(code envoye)")
            student_state.add_message(student_id, "tutor", "[success] deja validee par test.")
            return payload(reply, test_results=test_results)
        # PAS de validation immédiate : on attend la confirmation. Pour une
        # compétence auto-déclarée, la confirmation upgrade le statut.
        student_state.set_stage(student_id, skill_slug, "awaiting_confirmation")
        passed = sum(1 for t in test_results if t["passed"])
        if status == "auto_declared":
            observation = (
                f"Tous les tests passent ({passed}/{len(test_results)}). "
                "Cette compétence était acquise par déclaration : si tu confirmes, "
                "elle devient validée par test."
            )
        else:
            observation = (
                f"Tous les tests passent ({passed}/{len(test_results)}). "
                "Ton code répond correctement au problème."
            )
        reply = {
            "verdict": "awaiting_confirmation",
            "theory": "", "example": "", "problem": "", "hint": "",
            "observation": observation,
            "next_step": CONFIRMATION_QUESTION,
        }
        student_state.add_message(student_id, "user", message or "(code envoye)")
        student_state.add_message(
            student_id, "tutor",
            f"[awaiting_confirmation] {reply['observation']} {CONFIRMATION_QUESTION}"
        )
        return payload(reply, test_results=test_results)

    # --- 6. Recherche RAG (contexte pédagogique) pour la pratique guidée
    rag_query = message or (exercise.instructions if exercise else skill["title"] if skill else "")
    rag_chunks = _rag(rag_query, lang, skill)

    # --- 7. Prompt socratique -> Qwen (pratique guidée uniquement)
    profile = student_state.get_profile(student_id)
    user_message = build_user_message(
        student_name=profile["display_name"],
        language=LANGUAGE_LABELS.get(lang, lang),
        skill=skill,
        validated=validated,
        fragile=profile["fragile"],
        exercise={
            "title": exercise.title, "instructions": exercise.instructions,
        } if exercise else None,
        test_results=test_results,
        run_output=run_output,
        rag_chunks=[_chunk_for_context(c) for c in rag_chunks],
        student_message=message,
        code=code,
        history=student_state.get_history(student_id),
        attempts=attempts,
    )

    if not qwen.configured:
        tutor_reply = {
            "verdict": "partial",
            "theory": skill["theory"] if skill else "Configure ta cle Qwen pour activer le tuteur.",
            "hint": "Ajoute QWEN_API_KEY dans le fichier .env puis relance le serveur.",
            "observation": "Le modele Qwen n'est pas configure (pas de cle API).",
            "next_step": "Configurer .env et reessayer.",
        }
    else:
        try:
            raw = qwen.chat_json(SYSTEM_PROMPT, user_message)
            tutor_reply = {
                "verdict": raw.get("verdict", "partial"),
                "theory": raw.get("theory", ""),
                "hint": raw.get("hint", ""),
                "observation": raw.get("observation", ""),
                "next_step": raw.get("next_step", ""),
            }
        except Exception as exc:
            print(f"[tutor] Erreur API Qwen : {exc}")
            tutor_reply = {
                "verdict": "partial",
                "theory": skill["theory"] if skill else "",
                "hint": "Le modele est momentanement indisponible, reessaie dans un instant.",
                "observation": f"Erreur lors de l'appel au modele : {str(exc)[:200]}",
                "next_step": "Reessayer d'envoyer ton message.",
            }

    # --- 8. Notions fragiles (timeouts = boucles infinies probables)
    if exercise and test_results:
        for t in test_results:
            if not t["passed"] and t["timed_out"]:
                student_state.record_error(student_id, exercise.slug, "infinite_loop", "timeout")

    # --- 9. Persistance de la conversation
    student_state.add_message(student_id, "user", message or "(code envoye)")
    student_state.add_message(
        student_id, "tutor",
        f"[{tutor_reply['verdict']}] {tutor_reply['theory']} {tutor_reply['hint']}"
    )

    return payload(reply=tutor_reply, test_results=test_results, run_output=run_output)


def handle_run(*, student_id: int, language: str, code: str, exercise_slug: str | None = None):
    """Exécution simple (bouton 'Exécuter') : sans tests sauf si exercice demandé.
    Comme pour le chat, des tests réussis ne valident PAS la compétence :
    on passe en attente de confirmation."""
    exercise = get_exercise(exercise_slug) if exercise_slug else None
    if exercise:
        results = run_tests(language, code, exercise.tests)
        all_passed = bool(results) and all(r["passed"] for r in results)
        already_validated = exercise.slug in student_state.validated_skills(student_id)
        status = student_state.skill_status(student_id, exercise.slug)
        stage = None
        if all_passed and (not already_validated or status == "auto_declared"):
            # nouvelle compétence OU auto-déclarée : attente de confirmation
            student_state.set_stage(student_id, exercise.slug, "awaiting_confirmation")
            stage = "awaiting_confirmation"
        elif not all_passed:
            student_state.set_stage(student_id, exercise.slug, "practicing")
            stage = "practicing"
        else:
            for r in results:
                if r["timed_out"]:
                    student_state.record_error(student_id, exercise.slug, "infinite_loop", "timeout")
        return {"mode": "tests", "test_results": results, "all_passed": all_passed,
                "stage": stage}

    run = run_code(language, code)
    if not run.ok:
        kind, detail = classify_error(run.stderr, run.timed_out, language)
        student_state.record_error(student_id, None, kind, detail)
    return {"mode": "simple", "run": asdict(run), "stage": None}
