"""Unit tests for Thai date parsing (T004)."""
from datetime import date

import pytest

from timeline.dates import (
    parse_date_range,
    parse_thai_date,
    thai_to_arabic_digits,
    normalize_thai_text,
)


class TestThaiToArabicDigits:
    def test_converts_thai_digits(self):
        assert thai_to_arabic_digits("๑๒๓") == "123"
        assert thai_to_arabic_digits("๐") == "0"
        assert thai_to_arabic_digits("๒๕๖๘") == "2568"

    def test_keeps_arabic_and_text(self):
        assert thai_to_arabic_digits("ต.ค. 68") == "ต.ค. 68"
        assert thai_to_arabic_digits("") == ""


class TestNormalize:
    def test_collapses_spaced_thai_letters(self):
        # OCR ของ PDF ตัวอย่างให้ตัวอักษรเว้นวรรค
        assert normalize_thai_text("ต . ค . ๖ ๘") == "ต.ค. 68"


class TestParseThaiDate:
    # ปีงบประมาณ พ.ศ. ๒๕๗๐ → ต.ค.-ธ.ค. = 2568, ม.ค.-ก.ย. = 2569
    FY = 2570

    @pytest.mark.parametrize("abbr,month,be_short,ce_year", [
        ("ม.ค.", 1, "๖๙", 2026), ("ก.พ.", 2, "๖๙", 2026),
        ("มี.ค.", 3, "๖๙", 2026), ("เม.ย.", 4, "๖๙", 2026),
        ("พ.ค.", 5, "๖๙", 2026), ("มิ.ย.", 6, "๖๙", 2026),
        ("ก.ค.", 7, "๖๙", 2026), ("ส.ค.", 8, "๖๙", 2026),
        ("ก.ย.", 9, "๖๙", 2026), ("ต.ค.", 10, "๖๘", 2025),
        ("พ.ย.", 11, "๖๘", 2025), ("ธ.ค.", 12, "๖๘", 2025),
    ])
    def test_all_months_in_budget_cycle(self, abbr, month, be_short, ce_year):
        assert parse_thai_date(f"๑ {abbr} {be_short}", self.FY) == date(ce_year, month, 1)

    def test_abbreviated_year_oct_is_fy_minus_2(self):
        assert parse_thai_date("๑ ต.ค. ๖๘", self.FY) == date(2025, 10, 1)

    def test_abbreviated_year_dec_is_fy_minus_2(self):
        assert parse_thai_date("23 ธ.ค. ๖๘", self.FY) == date(2025, 12, 23)

    def test_abbreviated_year_jan_is_fy_minus_1(self):
        assert parse_thai_date("15 ม.ค. ๖๙", self.FY) == date(2026, 1, 15)

    def test_abbreviated_year_sep_is_fy_minus_1(self):
        assert parse_thai_date("30 ก.ย. ๖๙", self.FY) == date(2026, 9, 30)

    def test_full_buddhist_year(self):
        assert parse_thai_date("1 ตุลาคม 2568", self.FY) == date(2025, 10, 1)
        assert parse_thai_date("๑ ตุลาคม ๒๕๖๘", self.FY) == date(2025, 10, 1)

    def test_abbreviated_month_names(self):
        assert parse_thai_date("15 พ.ย. ๖๘", self.FY) == date(2025, 11, 15)
        assert parse_thai_date("3 มิ.ย. ๖๙", self.FY) == date(2026, 6, 3)
        assert parse_thai_date("25 ส.ค. ๖๙", self.FY) == date(2026, 8, 25)

    def test_unparseable_raises(self):
        with pytest.raises(ValueError):
            parse_thai_date("ไม่ใช่วันที่", self.FY)

    def test_invalid_day_raises(self):
        with pytest.raises(ValueError):
            parse_thai_date("32 ต.ค. ๖๘", self.FY)


class TestParseDateRange:
    FY = 2570

    def test_single_day(self):
        start, end = parse_date_range("๑ ต.ค. ๖๘", self.FY)
        assert start == date(2025, 10, 1)
        assert end is None

    def test_range_same_year(self):
        start, end = parse_date_range("๒ ต.ค. ๖๘ - ๒๓ ธ.ค. ๖๘", self.FY)
        assert start == date(2025, 10, 2)
        assert end == date(2025, 12, 23)

    def test_range_crossing_year(self):
        start, end = parse_date_range("๒๖ ธ.ค. ๖๘ - ๒๓ ม.ค. ๖๙", self.FY)
        assert start == date(2025, 12, 26)
        assert end == date(2026, 1, 23)

    def test_range_month_only_end(self):
        # "๑๕ พ.ย. - ๒๒ ธ.ค. ๖๘" — ปีย่ออยู่ท้าย ใช้ร่วมกัน
        start, end = parse_date_range("๑๕ พ.ย. - ๒๒ ธ.ค. ๖๘", self.FY)
        assert start == date(2025, 11, 15)
        assert end == date(2025, 12, 22)

    def test_sortable(self):
        dates = [
            parse_date_range("๑ ต.ค. ๖๘", self.FY),
            parse_date_range("๑๕ พ.ย. - ๒๒ ธ.ค. ๖๘", self.FY),
            parse_date_range("๑๐ ม.ค. ๖๙", self.FY),
        ]
        starts = [d[0] for d in dates]
        assert starts == sorted(starts)

    def test_duplicate_start_dates_remain_valid(self):
        first = parse_date_range("๑ ต.ค. ๖๘", self.FY)[0]
        second = parse_date_range("๑ ต.ค. ๖๘ - ๒๓ ธ.ค. ๖๘", self.FY)[0]
        assert first == second
