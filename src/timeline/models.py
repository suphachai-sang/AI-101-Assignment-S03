"""Data models for the Thai timeline feature (T005).

Mirrors specs/001-create-thai-timeline/data-model.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass
class Milestone:
    seq: int
    date_text: str
    start_date: date
    owner: str
    description: str
    end_date: Optional[date] = None
    group: str = ""
    needs_review: list[str] = field(default_factory=list)
    source_page: int | None = None

    def __post_init__(self) -> None:
        if self.seq < 1:
            raise ValueError("seq must be a positive integer")
        if not self.date_text:
            raise ValueError("date_text must not be empty")
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")


@dataclass
class ActivityGroup:
    name: str
    milestones: list[Milestone] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("group name must not be empty")


@dataclass
class ScheduleDocument:
    path: Path
    fiscal_year_be: int
    title: str
    groups: list[ActivityGroup] = field(default_factory=list)
    footer_notes: list[str] = field(default_factory=list)

    def all_milestones(self) -> list[Milestone]:
        return [m for g in self.groups for m in g.milestones]

    def sorted_milestones(self) -> list[Milestone]:
        return sorted(self.all_milestones(), key=lambda m: (m.start_date, m.seq))


@dataclass
class ExtractionReport:
    pages: int
    mean_confidence: float
    uncertain_terms: list[tuple[str, float, int]] = field(default_factory=list)
    milestone_count: int = 0

    def passes(self, threshold: float = 85.0) -> bool:
        return self.mean_confidence >= threshold
