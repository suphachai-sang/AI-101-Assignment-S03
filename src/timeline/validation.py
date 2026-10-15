"""Gate publication when extracted information has not been checked."""
from __future__ import annotations

from .models import ExtractionReport, ScheduleDocument

REQUIRED_GROUPS = {
    "การทบทวนและวางแผนงบประมาณ",
    "การจัดทำงบประมาณ",
    "การอนุมัติงบประมาณ",
}


def validate_document(
    document: ScheduleDocument,
    report: ExtractionReport,
    *,
    verified_source: bool,
    confidence_threshold: float = 85.0,
) -> list[str]:
    problems: list[str] = []
    if not report.passes(confidence_threshold):
        problems.append(
            f"ค่าความมั่นใจ OCR เฉลี่ย {report.mean_confidence:.1f} "
            f"ต่ำกว่าเกณฑ์ {confidence_threshold:g}"
        )
    if not document.all_milestones():
        problems.append("ไม่พบเหตุการณ์ที่สกัดได้จากเอกสาร")
    flagged = [m.seq for m in document.all_milestones() if m.needs_review]
    if flagged:
        problems.append("เหตุการณ์ที่ต้องตรวจทาน: " + ", ".join(map(str, flagged)))
    if not verified_source:
        problems.append("PDF นี้ยังไม่ผ่านการตรวจทานข้อมูลเหตุการณ์กับต้นฉบับ")
        found = {g.name for g in document.groups if g.milestones}
        if not REQUIRED_GROUPS.issubset(found) or len(document.all_milestones()) < 12:
            problems.append("สกัดเหตุการณ์จาก PDF ได้ไม่ครบ 3 กลุ่มหรือจำนวนน้อยผิดปกติ")
        if any(len(m.owner) < 3 for m in document.all_milestones()):
            problems.append("มีชื่อผู้รับผิดชอบที่อ่านไม่ได้อย่างน่าเชื่อถือ")
    return problems
