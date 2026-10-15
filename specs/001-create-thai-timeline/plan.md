# Implementation Plan: สร้างอินโฟกราฟิก Timeline ภาษาไทย

**Branch**: `001-create-thai-timeline` | **Date**: 2026-10-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-create-thai-timeline/spec.md`

## Summary

สร้างสคริปต์ CLI ภาษา Python ที่รับ PDF กำหนดการภาษาไทยแบบสแกน
(`HW03-Input.pdf` — ปฏิทินงบประมาณรายจ่ายประจำปีงบประมาณ พ.ศ. ๒๕๗๐) ทำ OCR
ด้วย Tesseract ภาษาไทย สกัดเหตุการณ์ (เลขลำดับ, วันที่ พ.ศ., ผู้รับผิดชอบ,
รายละเอียด) ครบ 3 กลุ่มกิจกรรม ตรวจสอบความมั่นใจของข้อมูล แล้วเรนเดอร์เป็นไฟล์
HTML เดียวแบบ self-contained ที่วาด timeline แนวนอนบน Canvas 2D ขนาด
1200×675 พิกเซล คล้ายรูปแบบภาพอ้างอิง `HW03-Output.jpg` ซึ่งเป็นปีงบประมาณ
พ.ศ. ๒๕๖๙ โดยยึดปี วันที่ และกิจกรรมจาก PDF เท่านั้น

## Technical Context

**Language/Version**: Python 3.13 (ทำงานได้ตั้งแต่ 3.11+)
**Primary Dependencies**: PyMuPDF 1.26.7 (PDF→ภาพ), pytesseract 0.3.13 +
Tesseract `script/Thai` (OCR), Sarabun Regular/Bold (ฝังฟอนต์ใน HTML),
standard library เท่านั้นสำหรับส่วนที่เหลือ; ผลลัพธ์ HTML ใช้ Canvas 2D API
ล้วน ไม่มี JS library ภายนอก
**Storage**: ไฟล์ (PDF input, HTML output, JSON report) — ไม่มีฐานข้อมูล
**Testing**: pytest (unit: parser/วันที่/กฎ validation; integration: pipeline
จริงกับ `HW03-Input.pdf`; contract: โครงสร้าง HTML/JSON output)
**Target Platform**: CLI บน macOS/Linux; ผลลัพธ์เปิดด้วยเบราว์เซอร์สมัยใหม่
**Project Type**: cli (สคริปต์ไฟล์เดียว + โมดูลทดสอบ)
**Performance Goals**: ประมวลผล PDF 3 หน้าเสร็จภายใน ~1 นาทีบนเครื่องทั่วไป
**Constraints**: HTML self-contained ไฟล์เดียว, canvas 1200×675 พอดี,
mean OCR confidence ≥ 85, ฝังฟอนต์ Sarabun ใน HTML และแสดงเลขอารบิกทุกตำแหน่ง
**Scale/Scope**: เอกสารกำหนดการรูปแบบเดียวกับตัวอย่าง ครอบคลุมเหตุการณ์
ที่มีวันที่ชัดเจนทั้ง 3 กลุ่มกิจกรรม; จำนวนที่แสดงต้องสัมพันธ์กับพื้นที่ 1200×675

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| หลักการ | แผนสอดคล้องอย่างไร | สถานะ |
|---|---|---|
| I. Source Fidelity | เก็บ `date_text` ดิบจากต้นฉบับ, แจ้งคำที่ OCR ไม่มั่นใจ (conf<60) ใน report, ไม่เดาค่า | ✅ |
| II. Thai Readability | ฟอนต์ไทยระบบ (Thonburi UI), ห่อข้อความด้วยการวัดจริง, เรียงเวลาเสมอ | ✅ |
| III. Focused, Separable | แยกโมดูล `ocr`, `parser`, `dates`, `render_html`; scope เฉพาะรูปแบบตัวอย่าง | ✅ |
| IV. Verifiable Output | pytest ครอบคลุม parser/วันที่/validation + integration กับ PDF จริง + ตรวจ HTML | ✅ |
| V. Explicit Errors | exit codes 2/3/4 แยกสาเหตุ, ข้อความไทย actionable, input ไม่ถูกแตะ | ✅ |

ไม่มีการละเมิดหลักการ ไม่ต้องบันทึก Complexity Tracking

## Project Structure

### Documentation (this feature)

```text
specs/001-create-thai-timeline/
├── plan.md              # ไฟล์นี้
├── research.md          # Phase 0 — การตัดสินใจทางเทคนิค (OCR, canvas, ฟอนต์, วันที่)
├── data-model.md        # Phase 1 — เอนทิตีและ validation rules
├── contracts/
│   └── cli-contract.md  # Phase 1 — สัญญา CLI, exit codes, ไฟล์
├── quickstart.md        # Phase 1 — วิธีรันและตรวจสอบ
├── checklists/
│   └── requirements.md  # checklist คุณภาพ spec
└── tasks.md             # Phase 2 (สร้างโดย /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── thai_timeline.py     # CLI entrypoint (argparse, orchestration)
├── timeline/
│   ├── __init__.py
│   ├── ocr.py           # PDF→ภาพ (PyMuPDF), OCR (pytesseract), confidence report
│   ├── dates.py         # แปลงเลขไทย, ตีความ พ.ศ. ย่อ, parse ช่วงวันที่
│   ├── parser.py        # แยกกลุ่มกิจกรรม/เหตุการณ์จากข้อความ OCR
│   ├── render_html.py   # สร้าง HTML self-contained พร้อม JSON + Canvas 2D
│   └── fonts/           # Sarabun Regular/Bold และ OFL.txt

tests/
├── unit/
│   ├── test_dates.py
│   ├── test_parser.py
│   └── test_validation.py
├── contract/
│   └── test_html_output.py
└── integration/
    └── test_pipeline.py  # รันจริงกับ HW03-Input.pdf ผ่าน CLI
```

**Structure Decision**: โปรเจกต์เดี่ยว (single project) — CLI entrypoint บาง
เรียก pipeline 4 ขั้นตอนที่แยกทดสอบได้ ตรงหลัก constitution ข้อ III

## แนวทางการออกแบบ (สรุปจาก research.md)

1. **OCR**: PyMuPDF render หน้า PDF ที่ 200 DPI → `pytesseract.image_to_data`
   ด้วย `script/Thai`, PSM 4 → เก็บข้อความ + confidence รายคำ
2. **Parsing**: แยกส่วนตามหัวข้อกลุ่มกิจกรรม → ตัดแถวเหตุการณ์ด้วยรูปแบบ
   "เลขลำดับ + วันที่" → ตัดหมายเหตุท้ายตารางออก (FR-008) และเทียบรายการ
   ที่สกัดได้กับรายการตรวจด้วยตาจาก PDF ทั้ง 3 หน้า
3. **วันที่**: แปลงเลขไทย→อารบิก → ตีความปี 2 หลักด้วยบริบทปีงบประมาณ (R4)
   → สร้าง start/end date สำหรับเรียงลำดับ
4. **Validation**: mean confidence ≥ 85 และเหตุการณ์จำเป็นไม่มี needs_review
   ตรวจปีงบประมาณ พ.ศ. ๒๕๗๐ กับหัวเรื่องและครบ 3 กลุ่มกิจกรรม
   มิฉะนั้น exit 3 พร้อม report (FR-009, FR-013)
5. **Render**: template HTML ฝัง `TimelineRenderModel` เป็น JSON → JavaScript
   วาดหัวเรื่อง แกนเวลา วางเลขคี่เหนือแกนและเลขคู่ใต้แกน ห่อข้อความด้วย
   `ctx.measureText` ฟอนต์ Sarabun ที่ฝังใน HTML และแปลงเลขไทยเป็นเลขอารบิก
   เฉพาะตอนวาด โดยเก็บข้อความต้นฉบับในข้อมูลฝังไว้

## ความเสี่ยงและการบรรเทา

| ความเสี่ยง | การบรรเทา |
|---|---|
| OCR เพี้ยนในบางคำ (สแกนเอียง) | เกณฑ์ confidence + needs_review + integration test เทียบค่าที่คาดหวัง |
| ตัวอักษรไทยซ้อนสระ/วรรณยุกต์บน canvas | ใช้ฟอนต์ไทย native + ทดสอบ render ผ่าน headless browser ใน integration |
| วันที่ข้ามปีตีความผิด | unit test เฉพาะ dates.py ครอบคลุมทุกเดือนและปีย่อ |
| คัดลอกปีและกิจกรรมจาก JPG ซึ่งเป็นคนละปีงบประมาณ | ตรวจปีในหัวเรื่องกับ PDF และใช้ JPG เฉพาะรูปลักษณ์ |
| ข้อความยาวล้นพื้นที่ | ห่อบรรทัดด้วย measureText + จำกัดจำนวนเหตุการณ์ที่แสดง (FR-005) |

## Post-Design Constitution Check

ประเมินซ้ำหลังออกแบบ Phase 1 เสร็จ: ทุกหลักการยังผ่าน ไม่มีการเปลี่ยนแปลง
ที่กระทบเกณฑ์ — ✅ PASS
