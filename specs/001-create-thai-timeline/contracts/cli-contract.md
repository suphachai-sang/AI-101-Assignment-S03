# Contract: CLI ของสคริปต์สร้าง Timeline Infographic

**Date**: 2026-10-15 | **Branch**: `001-create-thai-timeline`

สคริปต์เปิดเผยต่อผู้ใช้ผ่าน command-line interface เพียงช่องทางเดียว

## คำสั่ง

```bash
python3 src/thai_timeline.py <input.pdf> [--output <path.html>] [--force] [--report <path.json>]
```

| Argument/Flag | ความหมาย | ค่าเริ่มต้น |
|---|---|---|
| `input.pdf` (จำเป็น) | PDF กำหนดการภาษาไทยแบบสแกน | — |
| `--output <path.html>` | ตำแหน่งไฟล์ HTML ผลลัพธ์ | `<input-stem>-timeline.html` ในโฟลเดอร์เดียวกับ input |
| `--force` | อนุญาตเขียนทับไฟล์ output ที่มีอยู่ | ไม่อนุญาต (FR-012) |
| `--report <path.json>` | เขียน ExtractionReport เป็น JSON | แสดงสรุปบน stderr เท่านั้น |

## พฤติกรรมและ Exit Codes

| Exit code | เงื่อนไข | ผลข้างเคียง |
|---|---|---|
| 0 | สกัดและเรนเดอร์สำเร็จ ผ่านเกณฑ์ confidence | เขียนไฟล์ HTML (และ report ถ้าระบุ) |
| 2 | input ไม่มีอยู่ อ่านไม่ได้ หรือไม่ใช่ PDF | ไม่มีไฟล์ใดถูกเขียน |
| 3 | OCR ไม่ผ่านเกณฑ์ (mean conf < 85) หรือสกัดเหตุการณ์จำเป็นไม่ได้ | ไม่เขียน HTML; เขียน report ถ้าระบุ |
| 4 | output มีอยู่แล้วและไม่ได้ระบุ `--force` หรือ output ชี้ไปที่ input | ไม่มีไฟล์ใดถูกเขียน (FR-011, FR-012) |

## ข้อความแสดงข้อผิดพลาด

- เป็นภาษาไทย ระบุสาเหตุและสิ่งที่ผู้ใช้ควรทำต่อ (FR-009, FR-010)
- กรณีข้อมูลไม่มั่นใจ: ระบุคำ/ส่วนที่ต้องตรวจทานและหน้าที่พบ

## สัญญาด้านไฟล์

- ไฟล์ input ต้องไม่ถูกแก้ไข (FR-011)
- HTML ผลลัพธ์ต้องเป็นไฟล์เดียว self-contained เปิดด้วยเบราว์เซอร์สมัยใหม่ได้
  ทันที เรนเดอร์ canvas 1200×675 (FR-003, SC-001)
- ข้อมูลเหตุการณ์ฝังเป็น JSON ในไฟล์ตามโครงสร้าง `TimelineRenderModel` ใน
  `data-model.md`

## ตัวอย่าง

```bash
# ใช้ค่าเริ่มต้น
python3 src/thai_timeline.py HW03-Input.pdf

# ระบุ output และเขียนรายงาน
python3 src/thai_timeline.py HW03-Input.pdf --output dist/hw03.html --report dist/report.json

# เขียนทับผลลัพธ์เดิมอย่างชัดเจน
python3 src/thai_timeline.py HW03-Input.pdf --force
```
