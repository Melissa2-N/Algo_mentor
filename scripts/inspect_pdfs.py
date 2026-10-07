"""Inspecte la structure des PDF : tailles de police, titres detectes."""
import sys
from pathlib import Path

import pymupdf

pdf_dir = Path(__file__).resolve().parent.parent / "curriculum" / "pdfs"

for pdf_path in sorted(pdf_dir.glob("*.pdf")):
    doc = pymupdf.open(pdf_path)
    sizes: dict[float, int] = {}
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        sizes[round(span["size"], 1)] = sizes.get(round(span["size"], 1), 0) + len(text)
    if not sizes:
        print(f"== {pdf_path.name}: PAG vide ou scanne (aucun texte)")
        continue
    median_size = sorted(sizes.items(), key=lambda kv: -kv[1])[0][0]
    print(f"== {pdf_path.name}: {doc.page_count} pages, median={median_size}, "
          f"tailles={sorted(sizes.keys(), reverse=True)[:6]}")
    # Montre les lignes candidates titres (taille > median)
    shown = 0
    for pno, page in enumerate(doc):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                spans = line["spans"]
                if not spans:
                    continue
                text = "".join(s["text"] for s in spans).strip()
                size = max(s["size"] for s in spans)
                bold = any("bold" in s["font"].lower() for s in spans)
                if text and (size > median_size * 1.12 or (bold and size >= median_size)) and shown < 12:
                    print(f"   p{pno+1} [{round(size,1)}{'B' if bold else ''}] {text[:70]}")
                    shown += 1
        if shown >= 12:
            break
    doc.close()
