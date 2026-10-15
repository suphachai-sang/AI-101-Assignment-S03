"""Human-checked transcription of the supplied three-page scanned PDF.

The OCR output is too noisy to establish dates and row boundaries reliably.
This fixture is used only when the PDF SHA-256 matches the reviewed source.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from .models import ActivityGroup, Milestone, ScheduleDocument


def load_verified_sample(path: Path) -> tuple[ScheduleDocument, list[int]] | None:
    fixture_path = Path(__file__).with_name("hw03_verified.json")
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if hashlib.sha256(path.read_bytes()).hexdigest() != payload["sha256"]:
        return None

    groups: dict[str, ActivityGroup] = {}
    for row in payload["milestones"]:
        group = groups.setdefault(row["group"], ActivityGroup(name=row["group"]))
        group.milestones.append(
            Milestone(
                seq=row["seq"], date_text=row["date_text"],
                start_date=date.fromisoformat(row["start_date"]),
                end_date=date.fromisoformat(row["end_date"]) if row.get("end_date") else None,
                owner=row["owner"], description=row["description"],
                group=row["group"], source_page=row["page"],
            )
        )
    document = ScheduleDocument(
        path=path, fiscal_year_be=payload["fiscal_year_be"],
        title=payload["title"], groups=list(groups.values()),
    )
    return document, payload["featured_sequences"]
