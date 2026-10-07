"""Ingestion de documents PDF dans le RAG pgvector.

Pipeline :
1. Extraction texte + structure (PyMuPDF) : tailles de police, gras.
2. Detection des titres de sections (heuristique taille/gras/numerotation),
   filtrage de la table des matieres.
3. Chunking par section (fusion des sections courtes, decoupe des longues
   aux limites de paragraphes avec overlap). Jamais de coupe fixe aveugle.
4. Inference de concept + level : alias FR sur les 19 competences ->
   repli LLM (classification contrainte) -> overrides manuels.
5. Embedding bge-m3 (1024d) + insertion kb_chunks (kind=document),
   cohabite avec les chunks du curriculum JSON.

Usage :
  python scripts/ingest_documents.py --dry-run
  python scripts/ingest_documents.py                     # replace-documents
  python scripts/ingest_documents.py --mode append
  python scripts/ingest_documents.py --overrides overrides.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pymupdf  # noqa: E402

from app.db import execute, fetch_one, get_pool  # noqa: E402
from app.services.curriculum import SKILLS  # noqa: E402
from app.services.embeddings import embed  # noqa: E402
from app.services.qwen_client import qwen  # noqa: E402

PDF_DIR = BASE_DIR / "curriculum" / "pdfs"
CONFIG_PATH = BASE_DIR / "curriculum" / "pdf_sources.json"

# --- Parametres de chunking ---
MIN_CHUNK_CHARS = 300
MAX_CHUNK_CHARS = 2200
OVERLAP_CHARS = 200
MAX_HEADING_CHARS = 120

# ---------------------------------------------------------------------------
# Alias de concepts (FR) -> slugs des 19 competences
# ---------------------------------------------------------------------------
CONCEPT_ALIASES: dict[str, list[str]] = {
    "variables": ["variable", "affectation", "affecter une valeur", "identificateur"],
    "types": ["type de donnee", "les types", "entier", "flottant", "reel", "booleen",
              "chaine de caractere", "conversion", "caster", "type simple"],
    "conditions": ["condition", "alternative", "instruction si", "si alors sinon",
                   "branchement conditionnel", "if ", "test d'une condition"],
    "while_loop": ["tant que", "while", "boucle conditionnelle", "boucle non bornee"],
    "for_loop": ["boucle pour", "boucle bornee", "for ", "iterer", "iteration",
                 "compteur de boucle", "range("],
    "functions": ["fonction", "procedure", "sous-programme", "methode", "parametre",
                  "passage d'argument", "valeur de retour", "return"],
    "scope": ["portee", "scope", "variable globale", "variable locale"],
    "arrays": ["tableau", "liste", "array", "collection indexee", "vecteur"],
    "strings": ["chaine", "string", "texte", "caractere", "regex", "expression reguliere"],
    "dictionaries": ["dictionnaire", "table de hachage", "hash map", "table associative",
                     "cle/valeur", "association cle"],
    "stacks_queues": ["pile", "file ", "file d'attente", "stack", "queue", "lifo", "fifo"],
    "binary_search": ["dichotomique", "recherche binaire", "dichotomie"],
    "sorting": ["tri ", "trier", "tri par", "algorithme de tri", "permutation", "bulles"],
    "recursion": ["recursiv", "recurrence", "fonction recursive"],
    "complexity": ["complexite", "grand o", "o(n", "efficacite", "cout algorithmique",
                   "complexite temporelle"],
    "modular_design": ["modulaire", "decoupage", "decomposition", "sous-probleme",
                       "structurer un programme", "conception"],
    "error_handling": ["erreur", "exception", "gerer les erreurs", "try ", "robustesse",
                       "validation d'entree", "debugage", "debogage"],
    "file_io": ["fichier", "lecture/ecriture", "lire un fichier", "ecrire dans un fichier",
                "flux", "stream", "ouverture de fichier"],
    "mini_project": ["projet", "etude de cas", "travail pratique", "realisation complete",
                     "mise en pratique finale", "application complete"],
}

LEVEL_IN_TITLE = re.compile(r"niveau\s*([1-4])", re.IGNORECASE)
TOC_LINE = re.compile(r"\.{3,}\s*\d+\s*$|\s\d{1,3}\s*$")
HEADING_NUM = re.compile(
    r"^(?:(chapitre|partie|section)\s+)?"
    r"([IVX]+\.\d*|\d+(?:\.\d+)*)[.\s]?\s*(.*)$",
    re.IGNORECASE,
)
BARE_NUM = re.compile(r"^(?:chapitre|partie)?\s*([IVX]+\.?\d*|\d+(?:\.\d+)*)\.?$", re.IGNORECASE)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


# ---------------------------------------------------------------------------
# 1-2. Extraction + detection des titres
# ---------------------------------------------------------------------------
def extract_lines(doc: pymupdf.Document) -> list[dict]:
    """Toutes les lignes du document, dans l'ordre de lecture."""
    lines: list[dict] = []
    for pno, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        blocks.sort(key=lambda b: (round(b["bbox"][1], 1), round(b["bbox"][0], 1)))
        for block in blocks:
            for line in block.get("lines", []):
                spans = [s for s in line["spans"] if s["text"].strip()]
                if not spans:
                    continue
                lines.append({
                    "page": pno + 1,
                    "text": "".join(s["text"] for s in spans).strip(),
                    "size": max(s["size"] for s in spans),
                    "bold": any("bold" in s["font"].lower() for s in spans),
                    "y": line["bbox"][1],
                })
    return lines


def merge_numbering(lines: list[dict]) -> list[dict]:
    """Fusionne le numero de titre isole (ligne '1' puis 'Introduction')."""
    merged: list[dict] = []
    i = 0
    while i < len(lines):
        cur = dict(lines[i])
        if (merged and cur["text"] and BARE_NUM.match(cur["text"])
                and len(cur["text"]) <= 12 and i + 1 < len(lines)
                and abs(lines[i + 1]["size"] - cur["size"]) <= 1.0
                and len(lines[i + 1]["text"]) < MAX_HEADING_CHARS):
            cur["text"] = f"{cur['text']} {lines[i + 1]['text']}"
            i += 2
        else:
            i += 1
        merged.append(cur)
    return merged


def is_heading(line: dict, median: float, max_size: float) -> bool:
    text = line["text"]
    if not text or len(text) > MAX_HEADING_CHARS:
        return False
    if TOC_LINE.search(text):          # entree de table des matieres
        return False
    if normalize(text).startswith(("table des matiere", "sommaire", "page ")):
        return False
    numbered = HEADING_NUM.match(text) and text.rstrip(".") != text and bool(HEADING_NUM.match(text).group(2))
    size_heading = line["size"] >= max(median * 1.15, 13.0)
    bold_heading = line["bold"] and line["size"] >= median and line["size"] >= max_size - 6.0
    # ligne courte, non terminee par ponctuation de phrase
    clean_end = not text.endswith((".", ";", ",", ":"))
    return clean_end and (numbered or size_heading or bold_heading)


SKIP_TITLE_PATTERNS = ("tabledesmatiere", "tabledesmatieres", "sommaire",
                       "glossaire", "bibliographie", "referencesgenerales")


def is_skip_title(title: str) -> bool:
    return re.sub(r"[^a-z]", "", normalize(title))[:20] in SKIP_TITLE_PATTERNS


def build_sections(doc: pymupdf.Document) -> list[dict]:
    lines = merge_numbering(extract_lines(doc))
    sizes: dict[float, int] = {}
    for l in lines:
        sizes[round(l["size"], 1)] = sizes.get(round(l["size"], 1), 0) + len(l["text"])
    if not sizes:
        return []
    median = sorted(sizes.items(), key=lambda kv: -kv[1])[0][0]
    max_size = max(sizes)

    sections: list[dict] = []
    current = {"title": "Introduction", "page": 1, "parts": []}
    for line in lines:
        if is_heading(line, median, max_size):
            if current["parts"]:
                sections.append(current)
            current = {"title": line["text"], "page": line["page"], "parts": []}
        else:
            current["parts"].append(line["text"])
    if current["parts"]:
        sections.append(current)
    for s in sections:
        s["text"] = "\n".join(s.pop("parts")).strip()
    return [s for s in sections if s["text"] and not is_skip_title(s["title"])]


# ---------------------------------------------------------------------------
# 3. Chunking : fusion courte / decoupe longue avec overlap
# ---------------------------------------------------------------------------
def split_long(text: str) -> list[str]:
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]
    # 1) paragraphes ; 2) lignes ; 3) coupe dure avec overlap
    parts = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(parts) <= 1:
        parts = text.split("\n")
    if len(parts) <= 1:  # texte sur une seule ligne
        parts = [text[i:i + MAX_CHUNK_CHARS]
                 for i in range(0, len(text), MAX_CHUNK_CHARS - OVERLAP_CHARS)]
    chunks, buf = [], ""
    for part in parts:
        while len(part) > MAX_CHUNK_CHARS:  # paragraphe enormement long
            if buf:
                chunks.append(buf)
                buf = buf[-OVERLAP_CHARS:]
            chunks.append(part[:MAX_CHUNK_CHARS])
            part = part[MAX_CHUNK_CHARS - OVERLAP_CHARS:]
        if buf and len(buf) + len(part) + 2 > MAX_CHUNK_CHARS:
            chunks.append(buf)
            buf = (buf[-OVERLAP_CHARS:] + "\n" + part) if OVERLAP_CHARS else part
        else:
            buf = f"{buf}\n{part}" if buf else part
    if buf.strip():
        chunks.append(buf)
    return chunks


def build_chunks(sections: list[dict]) -> list[dict]:
    merged: list[dict] = []
    for s in sections:
        if merged and len(s["text"]) < MIN_CHUNK_CHARS:
            prev = merged[-1]
            prev["text"] += "\n\n" + s["text"]
            prev["page_end"] = s["page"]
        else:
            merged.append({**s, "page_end": s["page"]})
    chunks: list[dict] = []
    for s in merged:
        for i, part in enumerate(split_long(s["text"]), 1):
            chunks.append({
                "title": s["title"] if len(split_long(s["text"])) == 1
                         else f"{s['title']} (partie {i})",
                "page": s["page"],
                "text": part,
            })
    # elimine les residus non exploitables
    return [c for c in chunks if len(c["text"]) >= 60]


# ---------------------------------------------------------------------------
# 4. Inference concept + level
# ---------------------------------------------------------------------------
def detect_concept_by_rules(chunk: dict) -> str | None:
    title_n = normalize(chunk["title"])
    content_n = normalize(chunk["text"][:400])
    # Passe 1 : le titre prime (match le plus long gagne)
    best, best_len = None, 0
    for slug, aliases in CONCEPT_ALIASES.items():
        for alias in aliases:
            a = normalize(alias)
            if a in title_n and len(a) > best_len:
                best, best_len = slug, len(a)
    if best:
        return best
    # Passe 2 : sinon, contenu
    for slug, aliases in CONCEPT_ALIASES.items():
        for alias in aliases:
            a = normalize(alias)
            if a in content_n and len(a) > best_len:
                best, best_len = slug, len(a)
    return best


SKILLS_DESC = "\n".join(
    f"- {s['slug']}: {s['description']} (niveau {s['level']})" for s in SKILLS
)


def detect_by_llm(chunk: dict, language: str) -> dict | None:
    if not qwen.configured:
        return None
    system = (
        "Tu classifies des extraits de cours d'algorithmique.\n"
        f"Concepts possibles :\n{SKILLS_DESC}\n\n"
        'Réponds UNIQUEMENT en JSON : {"concept": "<slug ou null>", '
        '"level": <1-4 ou null>}. Choisis "level" si l\'extrait est clairement '
        "positionné sur un niveau du cursus, sinon null."
    )
    user = (
        f"Titre de section : {chunk['title']}\n"
        f"Langage du document : {language}\n\n"
        f"Contenu :\n{chunk['text'][:1200]}"
    )
    try:
        return qwen.chat_json(system, user, temperature=0.0)
    except Exception as exc:
        print(f"  [llm] classification echouee : {exc}")
        return None


def apply_overrides(chunks: list[dict], overrides_path: Path | None, file_name: str) -> None:
    if not overrides_path or not overrides_path.exists():
        return
    rules = json.loads(overrides_path.read_text(encoding="utf-8"))
    for rule in rules:
        if rule.get("file") and rule["file"] != file_name:
            continue
        needle = normalize(rule.get("title_contains", ""))
        for c in chunks:
            if needle and needle in normalize(c["title"]):
                if rule.get("concept"):
                    c["concept"], c["detected_by"] = rule["concept"], "override"
                if rule.get("level"):
                    c["level"] = rule["level"]


def infer_metadata(
    chunks: list[dict], language: str, use_llm: bool, max_llm: int
) -> tuple[list[dict], int]:
    llm_calls = 0
    skill_levels = {s["slug"]: s["level"] for s in SKILLS}
    for c in chunks:
        c["concept"] = detect_concept_by_rules(c)
        c["detected_by"] = "rule" if c["concept"] else "none"
        c["level"] = None
        m = LEVEL_IN_TITLE.search(c["title"])
        if m:
            c["level"] = int(m.group(1))
        if not c["concept"] and use_llm and llm_calls < max_llm:
            result = detect_by_llm(c, language)
            llm_calls += 1
            if result:
                if result.get("concept") in skill_levels:
                    c["concept"] = result["concept"]
                    c["detected_by"] = "llm"
                if result.get("level") in (1, 2, 3, 4):
                    c["level"] = result["level"]
        if c["level"] is None:
            c["level"] = skill_levels.get(c["concept"], 1)
    return chunks, llm_calls


# ---------------------------------------------------------------------------
# Configuration + langue
# ---------------------------------------------------------------------------
def detect_language(file_name: str) -> str:
    low = file_name.lower()
    if "python" in low:
        return "python"
    if "java" in low:
        return "java"
    if re.search(r"(^|[^a-z])c([^a-z]|$)", low) or "_c." in low:
        return "c"
    return "universal"


def load_config(pdf_dir: Path, config_path: Path) -> list[dict]:
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    entries = [
        {"file": p.name, "language": detect_language(p.name)}
        for p in sorted(pdf_dir.glob("*.pdf"))
    ]
    config_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Config generee automatiquement : {config_path}")
    return entries


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def process_pdf(
    pdf_path: Path, language: str, use_llm: bool, max_llm: int,
    overrides_path: Path | None, dry_run: bool,
) -> list[dict]:
    doc = pymupdf.open(pdf_path)
    sections = build_sections(doc)
    doc.close()
    chunks = build_chunks(sections)
    chunks, llm_calls = infer_metadata(chunks, language, use_llm, max_llm)
    apply_overrides(chunks, overrides_path, pdf_path.name)
    for c in chunks:
        c["source"] = pdf_path.name
        c["source_file"] = pdf_path.stem
        c["language"] = language

    print(f"\n=== {pdf_path.name} ({language}) : {len(chunks)} chunks, "
          f"{llm_calls} appels LLM")
    for c in chunks:
        print(f"  p{c['page']:>3} [{c['concept'] or '-':<15} n{c['level']} "
              f"{c['detected_by']:<8}] {c['title'][:60]} ({len(c['text'])} car.)")
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingestion PDF -> pgvector")
    parser.add_argument("--pdf-dir", type=Path, default=PDF_DIR)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--overrides", type=Path, default=None)
    parser.add_argument("--mode", choices=["replace-documents", "append"],
                        default="replace-documents")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-llm-classify", action="store_true")
    parser.add_argument("--max-llm-calls", type=int, default=40)
    args = parser.parse_args()

    entries = load_config(args.pdf_dir, args.config)
    all_chunks: list[dict] = []
    for entry in entries:
        pdf_path = args.pdf_dir / entry["file"]
        if not pdf_path.exists():
            print(f"!! {entry['file']} introuvable, ignore")
            continue
        all_chunks += process_pdf(
            pdf_path, entry["language"], not args.no_llm_classify,
            args.max_llm_calls, args.overrides, args.dry_run,
        )

    print(f"\nTotal : {len(all_chunks)} chunks")
    if args.dry_run:
        print("DRY-RUN : aucune insertion.")
        return

    if args.mode == "replace-documents":
        deleted = fetch_one(
            "SELECT count(*) AS n FROM kb_chunks WHERE metadata->>'kind' = 'document'"
        )["n"]
        execute("DELETE FROM kb_chunks WHERE metadata->>'kind' = 'document'")
        print(f"Chunks document supprimes : {deleted}")

    texts = [c["title"] + "\n" + c["text"] for c in all_chunks]
    print("Calcul des embeddings bge-m3...")
    vectors = embed(texts)

    for c, vec in zip(all_chunks, vectors):
        metadata = {
            "kind": "document", "source": c.get("source", ""),
            "page": c["page"], "detected_by": c["detected_by"],
            "language": c.get("language") or "universal",
        }
        execute(
            """
            INSERT INTO kb_chunks (concept, level, language, title, content, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s::vector)
            """,
            (
                c["concept"] or "general", c["level"],
                c.get("language") or "universal",
                f"{c['title']} — {c.get('source_file', '')}".strip(),
                c["text"], json.dumps(metadata),
                "[" + ",".join(f"{x:.7g}" for x in vec) + "]",
            ),
        )
    print(f"{len(all_chunks)} chunks document inseres dans kb_chunks.")
    get_pool().close()


if __name__ == "__main__":
    main()
