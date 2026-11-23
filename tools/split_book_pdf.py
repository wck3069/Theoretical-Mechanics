#!/usr/bin/env python3
"""Split manuscript/main.pdf into per-chapter PDFs using PDF bookmarks."""
from pypdf import PdfReader, PdfWriter
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "manuscript/main.pdf"
OUT = Path(__file__).resolve().parent.parent / "manuscript/pdf"
SLUGS = {1:"newton",2:"variational",3:"lagrangian",4:"oscillations",
         5:"rigid-body",6:"hamiltonian",7:"relativity"}

r = PdfReader(SRC)
starts = []
for item in r.outline:
    if not isinstance(item, list):
        starts.append(r.get_destination_page_number(item) + 1)  # 1-indexed
starts = sorted(set(starts))
assert len(starts) == 7, f"expected 7 chapter bookmarks, got {starts}"
total = len(r.pages)
OUT.mkdir(exist_ok=True)
for n, start in enumerate(starts, 1):
    end = starts[n] - 1 if n < len(starts) else total
    w = PdfWriter()
    for p in range(start - 1, end):
        w.add_page(r.pages[p])
    w.add_metadata({"/Title": f"理论力学 · 第{n}章", "/Author": "书稿"})
    f = OUT / f"ch{n:02d}-{SLUGS[n]}.pdf"
    with open(f, "wb") as fh:
        w.write(fh)
    print(f"{f.name}: pages {start}-{end}")
