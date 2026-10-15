# Data Model: สร้างอินโฟกราฟิก Timeline ภาษาไทย

**Date**: 2026-10-15 | **Branch**: `001-create-thai-timeline`

โมเดลข้อมูลนี้อธิบายเอนทิตีที่ไหลผ่าน pipeline: PDF → OCR → เหตุการณ์ที่
ตรวจสอบแล้ว → JSON ฝังใน HTML → canvas

## 1. ScheduleDocument (เอกสารกำหนดการ)

| Field | Type | คำอธิบาย | Validation |
|---|---|---|---|
| path | Path | ตำแหน่งไฟล์ PDF input | ต้องมีอยู่ อ่านได้ ไม่ถูกแก้ไข (FR-011) |
| fiscal_year_be | int | ปีงบประมาณ พ.ศ. จากหัวเรื่อง (เช่น 2570) | ต้องสกัดได้จากหัวเรื่อง; ถ้าไม่ได้ → ข้อผิดพลาดตาม FR-009 |
| title | str | หัวเรื่องปฏิทินงบประมาณ | ไม่ว่าง |
| groups | list[ActivityGroup] | กลุ่มกิจกรรมหลัก เรียงตามลำดับในเอกสาร | ≥ 1 กลุ่ม |
| footer_notes | list[str] | หมายเหตุท้ายตาราง (ไม่ใช่เหตุการณ์) | ห้ามสร้างเหตุการณ์จากค่านี้ (FR-008) |

## 2. ActivityGroup (กลุ่มกิจกรรม)

| Field | Type | คำอธิบาย | Validation |
|---|---|---|---|
| name | str | ชื่อกลุ่ม เช่น "การทบทวนและวางแผนงบประมาณ" | ไม่ว่าง |
| milestones | list[Milestone] | เหตุการณ์ในกลุ่ม | ≥ 0 รายการ |

สำหรับ `HW03-Input.pdf` ต้องมีครบ 3 กลุ่ม: การทบทวนและวางแผนงบประมาณ,
การจัดทำงบประมาณ, การอนุมัติงบประมาณ (SC-006)

## 3. Milestone (เหตุการณ์)

| Field | Type | คำอธิบาย | Validation |
|---|---|---|---|
| seq | int | หมายเลขลำดับจากตาราง | จำนวนเต็มบวก |
| date_text | str | ข้อความวันที่ดังต้นฉบับ เช่น "๑ ต.ค. ๖๘" หรือ "๒ ต.ค. ๖๘ - ๒๓ ธ.ค. ๖๘" | ไม่ว่าง |
| start_date | date | วันเริ่ม (ค.ศ. ภายใน) | ตีความได้ตาม R4; ไม่ได้ → flag review |
| end_date | date \| None | วันสิ้นสุดถ้าเป็นช่วง | ≥ start_date ถ้ามี |
| owner | str | หน่วยงานผู้รับผิดชอบ เช่น "คณะรัฐมนตรี", "สำนักงบประมาณ" | ไม่ว่าง |
| description | str | รายละเอียดกิจกรรม (อาจย่อแล้ว) | ห้ามเปลี่ยนข้อเท็จจริง (FR-007) |
| needs_review | list[str] | คำ/ส่วนที่ OCR ไม่มั่นใจ (conf < 60) | ค่าว่าง = ผ่านเกณฑ์ |
| source_page | int \| None | หน้า PDF ที่ตรวจสอบเหตุการณ์ | 1–3 สำหรับไฟล์ตัวอย่าง |

**กฎการตีความวันที่ (R4)**: แปลงเลขไทย→อารบิกก่อน ปี 2 หลักใช้บริบท
fiscal_year_be: เดือน ต.ค.–ธ.ค. = fiscal_year_be−2, เดือน ม.ค.–ก.ย. =
fiscal_year_be−1 (กรณีงบประมาณ พ.ศ. ๒๕๗๐ → ๒๕๖๘/๒๕๖๙)

**การเรียง**: เรียงตาม start_date, seq สำหรับการแสดงผล (FR-004)

## 4. ExtractionReport (รายงานการสกัด)

| Field | Type | คำอธิบาย |
|---|---|---|
| pages | int | จำนวนหน้าที่ OCR |
| mean_confidence | float | ค่า confidence เฉลี่ยทั้งเอกสาร (เกณฑ์ ≥ 85) |
| uncertain_terms | list[tuple[str, float, int]] | (คำ, conf, หน้า) ที่ conf < 60 |
| milestone_count | int | จำนวนเหตุการณ์ที่สกัดได้ |

ถ้า mean_confidence < 85 หรือเหตุการณ์จำเป็นมี needs_review ไม่ว่าง →
ระบบรายงานและไม่แสดง HTML ราวกับยืนยันแล้ว (FR-009)

## 5. TimelineRenderModel (โมเดลสำหรับเรนเดอร์)

ข้อมูลที่ฝังเป็น JSON ใน HTML:

```json
{
  "title": "ปฏิทินงบประมาณรายจ่ายประจำปีงบประมาณ พ.ศ. ๒๕๗๐",
  "canvas": {"width": 1200, "height": 675},
  "milestones": [
    {
      "seq": 1,
      "dateText": "๑ ต.ค. ๖๘",
      "startDate": "2025-10-01",
      "endDate": null,
      "owner": "คณะรัฐมนตรี",
      "group": "การทบทวนและวางแผนงบประมาณ",
      "description": "พิจารณาให้ความเห็นชอบแนวทางการจัดทำงบประมาณฯ",
      "sourcePage": 1
    }
  ]
}
```

ผลลัพธ์จริงมี `allMilestones` เพิ่มเติมสำหรับเก็บทุกแถวที่ตรวจทานจาก PDF
ส่วน `milestones` เก็บเฉพาะรายการที่เลือกแสดงบน canvas

## State Transitions

เอกสารไหลผ่านสถานะ: `RECEIVED → OCR_DONE → EXTRACTED → VALIDATED → RENDERED`
การเปลี่ยนผ่าน `VALIDATED → RENDERED` อนุญาตเฉพาะเมื่อ ExtractionReport
ผ่านเกณฑ์ มิฉะนั้นจบที่ `VALIDATED` พร้อมรายงานสิ่งที่ต้องตรวจทาน (FR-009)
