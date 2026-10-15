from datetime import date
from pathlib import Path

from timeline.models import ActivityGroup, ExtractionReport, Milestone, ScheduleDocument
from timeline.validation import validate_document


def document(needs_review: list[str] | None = None) -> ScheduleDocument:
    group = ActivityGroup(name="การทบทวนและวางแผนงบประมาณ")
    group.milestones.append(Milestone(
        seq=1, date_text="ต.ค. ๖๘", start_date=date(2025, 10, 1),
        owner="คณะรัฐมนตรี", description="เห็นชอบปฏิทินงบประมาณ",
        group=group.name, needs_review=needs_review or [],
    ))
    return ScheduleDocument(
        path=Path("input.pdf"), fiscal_year_be=2570, title="ปฏิทินงบประมาณ",
        groups=[group], footer_notes=["หมายเหตุ: ตามรัฐธรรมนูญ"],
    )


def test_low_confidence_blocks_output():
    problems = validate_document(
        document(), ExtractionReport(pages=1, mean_confidence=70), verified_source=True
    )
    assert any("ต่ำกว่าเกณฑ์" in p for p in problems)


def test_flagged_milestone_blocks_output():
    problems = validate_document(
        document(["วันที่อ่านไม่ชัด"]),
        ExtractionReport(pages=1, mean_confidence=95), verified_source=True,
    )
    assert any("เหตุการณ์ที่ต้องตรวจทาน: 1" in p for p in problems)


def test_unverified_pdf_blocks_output_even_when_ocr_score_is_high():
    problems = validate_document(
        document(), ExtractionReport(pages=1, mean_confidence=99), verified_source=False
    )
    assert any("ยังไม่ผ่านการตรวจทาน" in p for p in problems)
    assert any("ไม่ครบ 3 กลุ่ม" in p for p in problems)


def test_footer_note_does_not_count_as_milestone():
    doc = document()
    assert len(doc.all_milestones()) == 1
    assert "หมายเหตุ" not in doc.all_milestones()[0].description
