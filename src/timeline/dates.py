"""Thai date parsing (T006).

- แปลงเลขไทยเป็นอารบิกก่อน parse
- ปีย่อ 2 หลัก = ปี พ.ศ. ที่สอดคล้องกับปีงบประมาณในหัวเรื่อง
- ปีเต็ม 4 หลักเป็นปี พ.ศ. (CE = BE - 543)
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date

_THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")

MONTHS = {
    "ม.ค.": 1, "มกราคม": 1,
    "ก.พ.": 2, "กุมภาพันธ์": 2,
    "มี.ค.": 3, "มีนาคม": 3,
    "เม.ย.": 4, "เมษายน": 4,
    "พ.ค.": 5, "พฤษภาคม": 5,
    "มิ.ย.": 6, "มิถุนายน": 6,
    "ก.ค.": 7, "กรกฎาคม": 7,
    "ส.ค.": 8, "สิงหาคม": 8,
    "ก.ย.": 9, "กันยายน": 9,
    "ต.ค.": 10, "ตุลาคม": 10,
    "พ.ย.": 11, "พฤศจิกายน": 11,
    "ธ.ค.": 12, "ธันวาคม": 12,
}

# เดือนแบบย่อ เช่น "ต.ค." / "ตค" / OCR "ท.ค."
_MONTH_ABBR = {
    "มค": 1, "กพ": 2, "มค ": 3, "มค.": 1,
}

_DATE_RE = re.compile(
    r"(?P<day>\d{1,2})\s+(?P<month>[ก-๙]+(?:\.(?:[ก-๙]\.)?)?)\s*(?P<year>\d{2,4})"
)
_PARTIAL_DAY_MONTH_RE = re.compile(r"(?P<day>\d{1,2})\s+(?P<month>[ก-๙\.]+?)\.?$")


def thai_to_arabic_digits(text: str) -> str:
    return text.translate(_THAI_DIGITS)


def _fix_ocr_month(text: str) -> str:
    # OCR ตัวอย่างอ่าน "ต" เป็น "ท"
    text = re.sub(r"ท\.ค\.", "ต.ค.", text)
    text = re.sub(r"ท\.\s*ค\.", "ต.ค.", text)
    text = re.sub(r"ทค\.", "ต.ค.", text)
    return text


def _collapse_month_abbr(text: str) -> str:
    # "ม ิ ย ." → "มิ.ย." (3 ตัว) แล้ว "ต . ค ." → "ต.ค." (2 ตัว)
    text = re.sub(r"([ก-๙])\s+([ก-๙])\s+([ก-๙])\s*\.", r"\1\2.\3.", text)
    text = re.sub(r"([ก-๙])\s*\.\s*([ก-๙])\s*\.", r"\1.\2.", text)
    return text


def _collapse_spaced_words(text: str) -> str:
    """รวมคำภาษาไทยที่ OCR เว้นวรรคทุกตัวอักษร เช่น "ค ณะ ร ั ฐ" → "คณะรัฐ"."""
    return re.sub(r"(?<=[ก-๙])\s+(?=[ก-๙])", "", text)


def _fix_ocr_range_sep(text: str) -> str:
    # OCR ของตัวอย่างใส่ "อ ." คั่นช่วงวันที่ (อ่านเพี้ยนจาก "ถึง")
    text = re.sub(r"[-–]\s*อ\s*\.\s*(?=\d{1,2}\s)", "- ", text)
    return text


_DOW = ("อ", "อา", "อาทิตย์", "จ", "จันทร์", "พ", "พุธ", "พฤ", "พฤหัสบดี",
        "ศ", "ศุกร์", "ส", "เสาร์")


def _strip_day_of_week(text: str) -> str:
    # ตัดตัวย่อวันในสัปดาห์ที่ OCR ติดมากับแถว เช่น "อ ." "พ ." ที่อยู่ก่อนวันที่
    dow = "|".join(_DOW)
    text = re.sub(rf"^(?:{dow})\s*\.\s*(?=\d{{1,2}}\s)", "", text)
    return text


def normalize_thai_text(text: str) -> str:
    """Collapse OCR letter-spacing and normalize Unicode/digits."""
    text = unicodedata.normalize("NFC", text)
    text = thai_to_arabic_digits(text)
    text = _fix_ocr_month(text)
    text = _fix_ocr_range_sep(text)
    text = _strip_day_of_week(text)
    text = _collapse_spaced_words(text)
    # รวมตัวเลขที่ OCR แยก เช่น "๒ ๕" → "25"
    text = re.sub(r"(?<=\d)\s+(?=\d)", "", text)
    # รวมตัวอักษรย่อเดือนที่ถูกแยก เช่น "ต . ค ." → "ต.ค."
    text = _collapse_month_abbr(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _resolve_year_ce(year_digits: str, month: int, fiscal_year_be: int) -> int:
    y = int(year_digits)
    if y >= 100:  # ปี พ.ศ. เต็ม
        return y - 543
    candidates = [be for be in (fiscal_year_be - 2, fiscal_year_be - 1, fiscal_year_be)
                  if be % 100 == y]
    if len(candidates) != 1:
        raise ValueError(f"abbreviated Buddhist year {y:02d} does not match fiscal year {fiscal_year_be}")
    return candidates[0] - 543


def parse_thai_date(text: str, fiscal_year_be: int) -> date:
    t = normalize_thai_text(text)
    m = _DATE_RE.search(t)
    if not m:
        raise ValueError(f"unparseable Thai date: {text!r}")
    day = int(m.group("day"))
    month_name = m.group("month")
    if month_name not in MONTHS:
        raise ValueError(f"unknown Thai month in: {text!r}")
    month = MONTHS[month_name]
    year_ce = _resolve_year_ce(m.group("year"), month, fiscal_year_be)
    return date(year_ce, month, day)


def parse_date_range(text: str, fiscal_year_be: int) -> tuple[date, date | None]:
    t = normalize_thai_text(text)
    parts = re.split(r"\s*[-–]\s*", t, maxsplit=1)
    if len(parts) == 1:
        return parse_thai_date(t, fiscal_year_be), None
    left, right = parts
    # กรณีวันเริ่มเป็นตัวเลขล้วน เช่น "2-5 ก.ย. 26" → ยืมเดือน/ปีจากขวา
    right_full = _DATE_RE.search(right)
    if re.fullmatch(r"\d{1,2}", left) and right_full:
        left = f"{left} {right_full.group('month')} {right_full.group('year')}"
    elif _PARTIAL_DAY_MONTH_RE.match(left) and right_full:
        left = f"{left} {right_full.group('year')}"
    start = parse_thai_date(left, fiscal_year_be)
    end = parse_thai_date(right, fiscal_year_be)
    if end < start:
        raise ValueError(f"date range end before start: {text!r}")
    return start, end
