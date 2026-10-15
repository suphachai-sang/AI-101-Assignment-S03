# Tasks: สร้างอินโฟกราฟิก Timeline ภาษาไทย

**Input**: Design documents from `/specs/001-create-thai-timeline/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: รวมงานทดสอบไว้ตามหลัก constitution ข้อ IV (Verifiable Output)

**Organization**: งานถูกจัดกลุ่มตาม user story เพื่อให้พัฒนาและทดสอบแยกอิสระได้

## Format: `[ID] [P?] [Story] Description`

- **[P]**: ทำขนานได้ (ไฟล์ต่างกัน ไม่มี dependency ค้าง)
- **[Story]**: งานนี้เป็นของ user story ใด (US1, US2)
- ทุกงานระบุ file path ชัดเจนในรายละเอียด

## Path Conventions

- โครงสร้างเดี่ยวที่ repo root: `src/`, `tests/` ตาม plan.md

---

## Phase 1: Setup (โครงสร้างโปรเจกต์)

**Purpose**: สร้างโครงสร้างไฟล์และสภาพแวดล้อมพื้นฐาน

- [x] T001 สร้างโครงสร้างไดเรกทอรี `src/timeline/`, `tests/unit/`, `tests/contract/`, `tests/integration/`, `dist/` ตาม plan.md
- [x] T002 [P] สร้าง `src/timeline/__init__.py` (ว่าง) และไฟล์ `pytest.ini` ที่ repo root ตั้งค่า `testpaths = tests`
- [x] T003 [P] ตรวจความพร้อมสภาพแวดล้อม: สคริปต์ตรวจ Tesseract `script/Thai`, PyMuPDF, Python ≥ 3.11 ใน `tests/integration/conftest.py` (skip integration tests อย่างสุภาพถ้าไม่พร้อม)

---

## Phase 2: Foundational (ขั้นตอนกั้นทุก story)

**Purpose**: โมดูลวันที่และโมเดลข้อมูลที่ทุก story ใช้ร่วมกัน — ต้องเสร็จก่อนเริ่ม story ใดๆ

**⚠️ CRITICAL**: ห้ามเริ่มงาน user story จนกว่า phase นี้จะเสร็จ

- [x] T004 [P] เขียน unit tests สำหรับการแปลงเลขไทย→อารบิก, การตีความปี พ.ศ. ย่อตามบริบทปีงบประมาณ (ต.ค.–ธ.ค.=fy−2, ม.ค.–ก.ย.=fy−1), และการ parse วันเดียว/ช่วงวันที่ ใน `tests/unit/test_dates.py` (ครอบคลุมทุกเดือน, ข้ามปี, วันที่ซ้ำ)
- [x] T005 [P] สร้าง data classes `ScheduleDocument`, `ActivityGroup`, `Milestone`, `ExtractionReport` พร้อม validation พื้นฐานตาม data-model.md ใน `src/timeline/models.py`
- [x] T006 Implement `src/timeline/dates.py`: ฟังก์ชัน `thai_to_arabic_digits`, `parse_thai_date`, `parse_date_range(text, fiscal_year_be)`, และการ normalize เดือนไทยย่อ/เต็ม; ตีความ "๖๘" เป็น พ.ศ. ๒๕๖๘ และ "๖๙" เป็น พ.ศ. ๒๕๖๙ ตามปีงบประมาณ ๒๕๗๐ โดยไม่ใช้กฎ 2000+ปีสองหลัก ให้ผ่าน T004

**Checkpoint**: `python3 -m pytest tests/unit/test_dates.py -q` ผ่านทั้งหมด

---

## Phase 3: User Story 1 — สร้างอินโฟกราฟิกกำหนดการ (Priority: P1) 🎯 MVP

**Goal**: รับ `HW03-Input.pdf` แล้วสร้างไฟล์ HTML ที่เรนเดอร์ timeline canvas
1200×675 มีหัวเรื่อง เหตุการณ์ครบ 3 กลุ่มกิจกรรม เรียงเวลา อ่านภาษาไทยได้ชัดเจน

**Independent Test**: รัน `python3 src/thai_timeline.py HW03-Input.pdf --output dist/hw03.html --force`
แล้วเปิด `dist/hw03.html` ในเบราว์เซอร์ — เห็นหัวเรื่องปฏิทินงบประมาณ พ.ศ. ๒๕๗๐,
timeline แนวนอน, เหตุการณ์เรียงเวลา, ไม่มีข้อความล้นหรือทับกัน

### Tests สำหรับ User Story 1

- [x] T007 [P] [US1] เขียน unit tests สำหรับ parser: แยก 3 กลุ่มกิจกรรม, ตัดแถวเหตุการณ์ด้วยรูปแบบ "เลขลำดับ+วันที่", แยก owner/description, และตัดหมายเหตุท้ายตารางออก (FR-008) ใน `tests/unit/test_parser.py`
- [x] T008 [P] [US1] เขียน contract test สำหรับ HTML output: เป็นไฟล์เดียว, มี `<canvas>` 1200×675, มี JSON ฝังตาม TimelineRenderModel, ไม่มี reference ภายนอก (src/http) ใน `tests/contract/test_html_output.py`
- [x] T009 [P] [US1] ทำรายการเหตุการณ์จริงจาก PDF ทั้ง 3 หน้าเป็น fixture ใน `src/timeline/hw03_verified.json` แล้วเขียน integration test ใน `tests/integration/test_pipeline.py`: CLI exit 0, HTML มีปีงบประมาณ 2570, เหตุการณ์ครบ 3 กลุ่ม, เรียง start_date, input ไม่เปลี่ยน (checksum ก่อน/หลัง)

### Implementation สำหรับ User Story 1

- [x] T010 [P] [US1] Implement `src/timeline/ocr.py`: `render_pdf_pages(pdf_path, dpi=200)` ด้วย PyMuPDF, `ocr_pages(images)` ด้วย pytesseract `script/Thai` PSM 4, คืนข้อความรายหน้า + word confidence และ `ExtractionReport` (mean confidence, uncertain_terms conf<60 พร้อมเลขหน้า)
- [ ] T011 [US1] ยกระดับ `src/timeline/parser.py` ให้แยกตารางจาก OCR ที่เว้นวรรค/แตกแถวสำหรับ PDF อื่นได้ครบ 3 กลุ่ม; ไฟล์ตัวอย่างที่ตรวจทานแล้วใช้ `src/timeline/hw03_verified.json` แทนการเดาจาก OCR
- [x] T012 [US1] Implement `src/timeline/render_html.py`: `build_render_model(doc)` และ `render_html(model)` สร้าง HTML self-contained ที่ฝัง JSON + JavaScript วาดหัวเรื่อง, แกนเวลาแนวนอน, จุดเหตุการณ์สลับบน/ล่าง, ห่อข้อความไทยด้วย `ctx.measureText`, ฟอนต์ `"Thonburi UI", Tahoma, sans-serif` — ให้ผ่าน T008
- [x] T013 [US1] Implement `src/thai_timeline.py` CLI ตาม contracts/cli-contract.md: argparse (input, --output, --force, --report), orchestrate ocr→parse→validate→render, exit codes 0/2/3/4, เขียน report JSON เมื่อระบุ; ปีงบประมาณต้องสกัดได้จาก PDF ห้าม fallback เป็นค่าคงที่
- [x] T014 [US1] รัน integration test T009 ให้ผ่าน และตรวจภาพจริง: render `dist/hw03.html` ผ่าน headless browser/เบราว์เซอร์ ยืนยัน SC-001, SC-003, SC-004, SC-007 (ขนาด, ลำดับ, ไม่ล้น/ทับ, ปีถูกต้อง) และเปรียบเทียบรูปลักษณ์กับ `HW03-Output.jpg` โดยไม่คัดลอกข้อมูลจากภาพ

**Checkpoint**: User Story 1 ใช้งานได้จบ — `python3 -m pytest tests/ -q` ผ่านทั้งหมด และภาพที่ได้คล้ายภาพอ้างอิง

---

## Phase 4: User Story 2 — ระบุข้อมูลที่ต้องตรวจทาน (Priority: P2)

**Goal**: เมื่อ OCR/การสกัดไม่มั่นใจ ระบบแจ้งชัดเจนและไม่แสดงผลลัพธ์ราวกับ
ยืนยันแล้ว (FR-009, FR-010)

**Independent Test**: รัน CLI กับไฟล์ที่ไม่ใช่ PDF ที่อ่านได้ (เช่นไฟล์ว่าง/ภาพล้วน)
และกับ input ที่ถูกจำลอง confidence ต่ำ — ได้ exit code ถูกต้อง, ข้อความไทย
actionable, ไม่มีไฟล์ HTML ถูกเขียน

### Tests สำหรับ User Story 2

- [x] T015 [P] [US2] เขียน unit tests สำหรับ validation: mean confidence < 85 → ไม่ผ่าน, เหตุการณ์จำเป็นมี needs_review → รายงาน, หมายเหตุท้ายตารางไม่กลายเป็นเหตุการณ์ ใน `tests/unit/test_validation.py`
- [x] T016 [P] [US2] เพิ่ม integration tests: input ไม่มีอยู่ → exit 2; input ไม่ใช่ PDF → exit 2; output มีอยู่โดยไม่มี `--force` → exit 4; output ชี้ไปที่ input → exit 4 ใน `tests/integration/test_pipeline.py`

### Implementation สำหรับ User Story 2

- [x] T017 [US2] Implement เกต validation ใน `src/thai_timeline.py` + `src/timeline/validation.py`: ตรวจ ExtractionReport (mean ≥ 85), รวม needs_review ของเหตุการณ์, สร้างข้อความแจ้งภาษาไทยที่ระบุคำและหน้าที่ต้องตรวจทาน, exit 3 เมื่อไม่ผ่าน — ให้ผ่าน T015
- [x] T018 [US2] เพิ่มการป้องกันไฟล์ใน CLI: ตรวจ input มีอยู่/เป็น PDF (exit 2), output ซ้ำโดยไม่มี --force หรือ output==input (exit 4) ตาม contract — ให้ผ่าน T016

**Checkpoint**: ทั้ง US1 และ US2 ทำงานอิสระและผ่านการทดสอบทั้งหมด

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: ปรับปรุงข้ามหลาย story

- [x] T019 [P] ปรับแต่งเลย์เอาต์ timeline (แถบหัวเรื่อง สี ช่วงเดือน แกนกลาง เลขคี่ด้านบน เลขคู่ด้านล่าง ระยะห่าง และขนาดฟอนต์) ใน `src/timeline/render_html.py` ให้ใกล้รูปลักษณ์ `HW03-Output.jpg` โดยยึดข้อมูลปี 2570 จาก PDF และยังผ่าน contract tests
- [x] T020 [P] อัปเดต `quickstart.md` ให้ตรงคำสั่งจริง และเพิ่มตัวอย่างภาพผลลัพธ์ใน `dist/`
- [x] T021 รัน `python3 -m pytest tests/ -q` ชุดเต็ม + ตรวจ `git diff --check` และสรุปผล SC-001 ถึง SC-008 ใน `specs/001-create-thai-timeline/verification.md`
- [ ] T022 เขียนบันทึกเปรียบเทียบ prompt ธรรมดากับ Spec Kit workflow และ reflection 150–200 คำตาม assignment ใน `reflection.md` ที่ repo root

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ไม่มี dependency — เริ่มได้ทันที
- **Foundational (Phase 2)**: ขึ้นกับ Setup เสร็จ — กั้นทุก user story
- **User Story 1 (Phase 3)**: ขึ้นกับ Foundational เสร็จ
- **User Story 2 (Phase 4)**: ขึ้นกับ Foundational เสร็จ — ขยาย US1 แต่ทดสอบแยกได้
- **Polish (Phase 5)**: ขึ้นกับ story ที่ต้องการเสร็จ (ขั้นต่ำ US1)

### User Story Dependencies

- **US1 (P1)**: เริ่มหลัง Foundational — ไม่ขึ้นกับ story อื่น
- **US2 (P2)**: เริ่มหลัง Foundational — ใช้โมดูลเดียวกับ US1 แต่เพิ่มเกต validation แยก; ทำขนานกับ US1 ได้ถ้าแบ่งไฟล์ (`validation.py` vs `parser.py`/`render_html.py`)

### Within Each User Story

- Tests (T007–T009, T015–T016) ก่อน implementation เมื่อเป็นไปได้
- โมดูล (`ocr.py`, `parser.py`) ก่อน orchestration (`thai_timeline.py`)
- implementation ก่อน integration/render ตรวจจริง

### Parallel Opportunities

- งาน Setup ทั้งหมดที่ติด [P] ทำขนานได้
- T004, T005 (Foundational) ขนานกันได้ — T006 ต้องรอ T004
- ใน US1: T007, T008, T009 (tests) ขนานกัน; T010 ขนานกับ T011 ได้ (อินเทอร์เฟซผ่าน models.py)
- ใน US2: T015, T016 ขนานกัน; ขนานกับงาน US1 บางส่วนได้ (ต่างไฟล์)

```text
ตัวอย่างขนาน (US1):
  T007 test_parser.py  ∥  T008 test_html_output.py  ∥  T009 test_pipeline.py
ตัวอย่างขนาน (หลัง Foundational):
  T010 ocr.py  ∥  T011 parser.py (ตกลงอินเทอร์เฟซ Milestone ผ่าน models.py ก่อน)
```

---

## Implementation Strategy

### MVP First (User Story 1 เท่านั้น)

1. ทำ Phase 1: Setup → Phase 2: Foundational ให้เสร็จ
2. ทำ Phase 3: US1 จนจบ → ตรวจ independent test (เปิด HTML เห็น timeline ถูกต้อง)
3. **STOP และ VALIDATE**: ทดสอบ US1 แยกอิสระ — ได้ MVP ที่สาธิตได้แล้ว
4. ค่อยทำ US2 (validation) และ Polish ถ้ามีเวลา

### Incremental Delivery

1. Setup + Foundational → รากฐานพร้อม
2. US1 → ทดสอบอิสระ → ใช้งานได้จริง (MVP!)
3. US2 → เพิ่มความน่าเชื่อถือ → ทดสอบอิสระ
4. Polish → ปรับภาพ/เอกสาร/reflection → ส่งงาน

---

## Summary

- **Total tasks**: 22 (T001–T022)
- **US1**: 8 งาน (T007–T014) | **US2**: 4 งาน (T015–T018)
- **Setup**: 3 | **Foundational**: 3 | **Polish**: 4
- **Parallel opportunities**: T002∥T003, T004∥T005, T007∥T008∥T009, T010∥T011, T015∥T016, T019∥T020
- **Independent test criteria**:
  - US1: รัน CLI กับ HW03-Input.pdf ได้ HTML ที่เปิดแล้วเห็น timeline ครบ 3 กลุ่ม เรียงเวลา ไม่ล้น/ทับ
  - US2: รัน CLI กับ input ผิดปกติได้ exit code ถูก + ข้อความไทย ไม่เขียน HTML
- **Suggested MVP scope**: User Story 1 (T001–T014)
