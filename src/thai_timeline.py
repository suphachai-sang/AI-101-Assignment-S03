#!/usr/bin/env python3
"""CLI: สร้างอินโฟกราฟิก timeline ภาษาไทยจาก PDF กำหนดการแบบสแกน (T013).

ตาม contracts/cli-contract.md — exit codes: 0 สำเร็จ, 2 input ผิด, 3 ไม่ผ่าน
เกณฑ์ OCR/validation, 4 output ชน/ไม่ปลอดภัย
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from timeline.ocr import ocr_pages, render_pdf_pages
from timeline.parser import parse_document
from timeline.render_html import build_render_model, render_html
from timeline.sample_data import load_verified_sample
from timeline.dates import normalize_thai_text
from timeline.validation import validate_document

EXIT_OK = 0
EXIT_INPUT = 2
EXIT_VALIDATION = 3
EXIT_OUTPUT = 4

_CONFIDENCE_THRESHOLD = 85.0


def _err(msg: str) -> None:
    print(f"ข้อผิดพลาด: {msg}", file=sys.stderr)


def _extract_fiscal_year(pages_text: list[str]) -> int | None:
    import re

    for text in pages_text:
        normalized = normalize_thai_text(text)
        m = re.search(r"พ\.?\s*ศ\.?\s*(25\d{2})", normalized)
        if m:
            return int(m.group(1))
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="สร้างอินโฟกราฟิก timeline HTML จาก PDF กำหนดการภาษาไทย"
    )
    ap.add_argument("input", help="PDF กำหนดการภาษาไทยแบบสแกน")
    ap.add_argument("--output", help="ตำแหน่งไฟล์ HTML ผลลัพธ์")
    ap.add_argument("--force", action="store_true", help="อนุญาตเขียนทับ output")
    ap.add_argument("--report", help="เขียน ExtractionReport เป็น JSON")
    args = ap.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        _err(f"ไม่พบไฟล์ input: {input_path}")
        return EXIT_INPUT
    if input_path.suffix.lower() != ".pdf":
        _err(f"ไฟล์ input ต้องเป็น PDF: {input_path}")
        return EXIT_INPUT

    output_path = (
        Path(args.output)
        if args.output
        else input_path.with_name(f"{input_path.stem}-timeline.html")
    )
    if output_path.resolve() == input_path.resolve():
        _err("ตำแหน่ง output ต้องไม่ชี้ไปที่ไฟล์ input")
        return EXIT_OUTPUT
    if output_path.exists() and not args.force:
        _err(
            f"ไฟล์ output มีอยู่แล้ว: {output_path} "
            "(ใช้ --force หากตั้งใจเขียนทับ)"
        )
        return EXIT_OUTPUT

    try:
        images = render_pdf_pages(input_path)
    except Exception as exc:  # PDF เสีย/อ่านไม่ได้
        _err(f"อ่าน PDF ไม่ได้ ({input_path}): {exc}")
        return EXIT_INPUT

    pages_text, report = ocr_pages(images)

    verified = load_verified_sample(input_path)
    if verified is not None:
        doc, featured_sequences = verified
    else:
        featured_sequences = None
        fiscal_year = _extract_fiscal_year(pages_text)
        doc = parse_document(pages_text, fiscal_year, path=input_path) if fiscal_year else None
    if doc is None:
        _err("อ่านปีงบประมาณจากหัวเรื่องไม่ได้ กรุณาตรวจทาน PDF ต้นฉบับ")
        return EXIT_VALIDATION
    report.milestone_count = len(doc.all_milestones())

    report_payload = {
        "pages": report.pages,
        "mean_confidence": round(report.mean_confidence, 2),
        "milestone_count": report.milestone_count,
        "verified_source": verified is not None,
        "uncertain_terms": [
            {"term": t, "confidence": c, "page": p}
            for t, c, p in report.uncertain_terms
        ],
    }
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    problems = validate_document(
        doc, report, verified_source=verified is not None,
        confidence_threshold=_CONFIDENCE_THRESHOLD,
    )
    if problems:
        _err("; ".join(problems))
        if report.uncertain_terms:
            preview = ", ".join(
                f'"{t}"(หน้า {p})' for t, _, p in report.uncertain_terms[:10]
            )
            print(f"คำที่ต้องตรวจทาน: {preview}", file=sys.stderr)
        print("แนะนำ: ตรวจทานเอกสารต้นฉบับ หรือสแกนใหม่ให้คมชัดขึ้น", file=sys.stderr)
        return EXIT_VALIDATION

    model = build_render_model(doc, featured_sequences)
    html = render_html(model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    print(f"สร้างไฟล์เรียบร้อย: {output_path}")
    print(
        f"สกัดได้ {report.milestone_count} เหตุการณ์ จาก {report.pages} หน้า "
        f"(confidence เฉลี่ย {report.mean_confidence:.1f})"
    )
    if verified is not None:
        print("ข้อมูลเหตุการณ์ใช้รายการที่ตรวจทานกับ PDF ต้นฉบับแล้ว")
    if report.uncertain_terms:
        print(
            f"หมายเหตุ: OCR ดิบมี {len(report.uncertain_terms)} คำที่ความมั่นใจต่ำ "
            "(ดูใน report)"
        )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
