"""Unit tests for schedule document parsing (T007)."""
from datetime import date

from timeline.parser import parse_document


FY = 2570

SAMPLE = [
    # หน้า 1
    "ปฏิทินงบประมาณรายจ่ายประจำปีงบประมาณ พ.ศ. ๒๕๗๐\n"
    "ลำดับ วัน เดือน ปี ขั้นตอนและกิจกรรม\n"
    "การทบทวนและวางแผนงบประมาณ\n"
    "๑ ต.ค. ๖๘ คณะรัฐมนตรี พิจารณาให้ความเห็นชอบแนวทางการจัดทำงบประมาณและปฏิทินงบประมาณรายจ่ายประจำปีงบประมาณ พ.ศ. ๒๕๗๐\n"
    "๒ ต.ค. ๖๘ - ๒๓ ธ.ค. ๖๘ หน่วยรับงบประมาณ จัดทำรายงานผลการใช้จ่ายงบประมาณ\n",
    # หน้า 2
    "การจัดทำงบประมาณ\n"
    "๘ พ.ย. ๖๘ - ๒๒ ธ.ค. ๖๘ หน่วยรับงบประมาณ จัดทำรายละเอียดคำของบประมาณ\n"
    "๕ ม.ค. - ๒๓ ม.ค. ๖๙ สำนักงบประมาณ พิจารณารายละเอียดคำของบประมาณ\n",
    # หน้า 3
    "การอนุมัติงบประมาณ\n"
    "๒-๕ ก.ย. ๖๙ สภาผู้แทนราษฎร พิจารณาร่างพระราชบัญญัติงบประมาณ วาระที่ ๑\n"
    "หมายเหตุ: ตามรัฐธรรมนูญแห่งราชอาณาจักรไทย พุทธศักราช ๒๕๖๐\n"
    "- สภาผู้แทนราษฎรมีเวลาพิจารณาให้แล้วเสร็จภายใน ๑๐๕ วัน\n",
]


class TestGroups:
    def test_extracts_three_groups(self):
        doc = parse_document(SAMPLE, FY, path="HW03-Input.pdf")
        names = [g.name for g in doc.groups]
        assert "การทบทวนและวางแผนงบประมาณ" in names
        assert "การจัดทำงบประมาณ" in names
        assert "การอนุมัติงบประมาณ" in names

    def test_footer_notes_not_milestones(self):
        doc = parse_document(SAMPLE, FY, path="HW03-Input.pdf")
        all_desc = " ".join(m.description for m in doc.all_milestones())
        assert "รัฐธรรมนูญ" not in all_desc
        assert "105" not in all_desc and "๑๐๕" not in all_desc


class TestMilestones:
    def test_single_date(self):
        doc = parse_document(SAMPLE, FY, path="x.pdf")
        singles = [m for m in doc.all_milestones() if m.end_date is None]
        m = next(m for m in singles if m.start_date == date(2025, 10, 1))
        assert m.end_date is None
        assert "คณะรัฐมนตรี" in m.owner

    def test_date_range(self):
        doc = parse_document(SAMPLE, FY, path="x.pdf")
        rng = [m for m in doc.all_milestones() if m.end_date is not None]
        assert any(
            m.start_date == date(2025, 10, 2) and m.end_date == date(2025, 12, 23)
            for m in rng
        )

    def test_cross_year_range(self):
        doc = parse_document(SAMPLE, FY, path="x.pdf")
        assert any(
            m.start_date == date(2026, 1, 5) and m.end_date == date(2026, 1, 23)
            for m in doc.all_milestones()
        )

    def test_sorted_chronologically(self):
        doc = parse_document(SAMPLE, FY, path="x.pdf")
        starts = [m.start_date for m in doc.sorted_milestones()]
        assert starts == sorted(starts)

    def test_group_assignment(self):
        doc = parse_document(SAMPLE, FY, path="x.pdf")
        for g in doc.groups:
            for m in g.milestones:
                assert m.group == g.name

    def test_row_number_owner_and_description_are_separate(self):
        doc = parse_document(SAMPLE, FY, path="x.pdf")
        first = next(m for m in doc.all_milestones() if m.start_date == date(2025, 10, 1))
        assert first.seq == 1
        assert first.owner == "คณะรัฐมนตรี"
        assert first.description.startswith("พิจารณาให้ความเห็นชอบ")


class TestTitle:
    def test_title_extracted(self):
        doc = parse_document(SAMPLE, FY, path="x.pdf")
        assert "ปฏิทินงบประมาณ" in doc.title
