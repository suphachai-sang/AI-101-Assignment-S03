"""OCR pipeline: PDF pages → Thai text + confidence report (T010).

Reconstructs page text line-by-line using Tesseract's block/par/line structure
so the parser can split milestone rows (OCR of the sample scan spaces every
letter, so word streams lose row boundaries).
"""
from __future__ import annotations

from pathlib import Path

import pytesseract
from PIL import Image

from .models import ExtractionReport

_OCR_LANG = "script/Thai"
_OCR_CONFIG = "--psm 4"


def render_pdf_pages(pdf_path: str | Path, dpi: int = 200) -> list[Image.Image]:
    """Render each PDF page to a PIL Image at the given DPI using PyMuPDF."""
    import fitz  # PyMuPDF

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ input: {pdf_path}")
    images: list[Image.Image] = []
    with fitz.open(pdf_path) as doc:
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        for page in doc:
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            images.append(img)
    return images


def ocr_pages(images: list[Image.Image]) -> tuple[list[str], ExtractionReport]:
    """OCR page images; return per-page line text and a confidence report."""
    pages_text: list[str] = []
    all_confs: list[int] = []
    uncertain: list[tuple[str, float, int]] = []

    for idx, img in enumerate(images, start=1):
        data = pytesseract.image_to_data(
            img, lang=_OCR_LANG, config=_OCR_CONFIG,
            output_type=pytesseract.Output.DICT,
        )
        lines: dict[tuple[int, int, int], list[str]] = {}
        for i, word in enumerate(data["text"]):
            w = word.strip()
            if not w:
                continue
            c = int(data["conf"][i])
            if c < 0:
                continue
            key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
            lines.setdefault(key, []).append(w)
            all_confs.append(c)
            if c < 60:
                uncertain.append((w, float(c), idx))
        page_lines = [" ".join(lines[k]) for k in sorted(lines)]
        pages_text.append("\n".join(page_lines))

    mean_conf = sum(all_confs) / len(all_confs) if all_confs else 0.0
    report = ExtractionReport(
        pages=len(images), mean_confidence=mean_conf, uncertain_terms=uncertain
    )
    return pages_text, report
