"""Parse OCR pages into a ScheduleDocument (T011).

The scanned budget-calendar PDF has a table per page with columns
ลำดับ | วัน เดือน ปี | ขั้นตอนและกิจกรรม, section headers for the three
activity groups, and footer notes that must NOT become milestones (FR-008).

Rows are detected by a leading parseable date before section headers are
considered, because a row's description text may contain group keywords.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from .dates import normalize_thai_text, parse_date_range
from .models import ActivityGroup, Milestone, ScheduleDocument

_GROUP_PATTERNS = [
    ("การทบทวนและวางแผนงบประมาณ",
     re.compile(r"ท\s*บ\s*ท\s*ว\s*น|ทบทวน")),
    ("การจัดทำงบประมาณ",
     re.compile(r"การจัดท[ํำ]\s*งบ\s*ประมาณ")),
    ("การอนุมัติงบประมาณ",
     re.compile(r"^การอนุมัติ\s*งบ\s*ประมาณ$")),
]

_FOOTER_MARKERS = ("หมายเหตุ", "ตามรัฐธรรมนูญ", "- สภาผู้แทน", "- วุฒิสภา")

_KNOWN_OWNERS = [
    "คณะรัฐมนตรี", "นายกรัฐมนตรี", "สำนักงบประมาณ", "สภาผู้แทนราษฎร",
    "วุฒิสภา", "กระทรวงการคลัง", "หน่วยรับงบประมาณ", "จังหวัด",
    "คณะกรรมการนโยบายการเงินการคลังของรัฐ", "สำนักเลขาธิการคณะรัฐมนตรี",
]

_DAY = r"\d{1,2}"
_MON = r"[ก-๙]+\.(?:[ก-๙]\.)?"
_DATE_PREFIX = (
    r"(?:" + _DAY + r"\s*[-–]\s*)?" + _DAY + r"\s*" + _MON + r"(?:\s*\d{2,4})?"
    r"(?:\s*[-–]\s*" + _DAY + r"\s*" + _MON + r"(?:\s*\d{2,4})?)?"
)
_ROW_RE = re.compile(r"^(?P<date>" + _DATE_PREFIX + r")\s+(?P<rest>.+)$")


def _is_footer(line: str) -> bool:
    return any(marker in line for marker in _FOOTER_MARKERS)


def _match_group(line: str) -> str | None:
    for name, pat in _GROUP_PATTERNS:
        if pat.search(line):
            return name
    return None


def _split_owner(rest: str) -> tuple[str, str]:
    for owner in _KNOWN_OWNERS:
        if rest.startswith(owner):
            return owner, rest[len(owner):].strip()
    parts = rest.split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", rest


def parse_document(
    pages_text: list[str], fiscal_year_be: int, path: str | Path = ""
) -> ScheduleDocument:
    doc = ScheduleDocument(
        path=Path(path), fiscal_year_be=fiscal_year_be, title=""
    )
    current: ActivityGroup | None = None
    title_found = False

    for raw in pages_text:
        for line in raw.splitlines():
            line = normalize_thai_text(line)
            if not line:
                continue

            if not title_found and "ปฏิทินงบประมาณ" in line:
                doc.title = line
                title_found = True
                continue
            if "ลำดับ" in line and "วัน" in line:
                continue
            if _is_footer(line):
                doc.footer_notes.append(line)
                continue

            # แถวเหตุการณ์: วันที่อยู่ต้นและ parse ได้ (ก่อนตรวจหัวข้อกลุ่ม)
            m = _ROW_RE.match(line)
            if m:
                date_text = m.group("date").strip(" |")
                try:
                    start, end = parse_date_range(date_text, fiscal_year_be)
                except ValueError:
                    start = end = None
                if start is not None:
                    owner, description = _split_owner(m.group("rest").strip(" |"))
                    if current is None:
                        current = ActivityGroup(name="อื่นๆ")
                        doc.groups.append(current)
                    current.milestones.append(
                        Milestone(
                            seq=len(doc.all_milestones()) + 1,
                            date_text=date_text,
                            start_date=start,
                            end_date=end,
                            owner=owner,
                            description=description,
                            group=current.name,
                        )
                    )
                    continue

            # หัวข้อกลุ่มกิจกรรม (เฉพาะบรรทัดที่ไม่ใช่แถวเหตุการณ์)
            group_name = _match_group(line)
            if group_name and not any(g.name == group_name for g in doc.groups):
                current = ActivityGroup(name=group_name)
                doc.groups.append(current)
                continue
            if group_name:
                current = next(g for g in doc.groups if g.name == group_name)
                continue

    return doc
