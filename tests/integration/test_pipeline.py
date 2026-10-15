"""Exercise the CLI against the actual scanned assignment PDF."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "src" / "thai_timeline.py"
PDF = ROOT / "HW03-Input.pdf"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        cwd=ROOT, text=True, capture_output=True, timeout=90,
    )


def test_real_pdf_renders_verified_schedule(tmp_path: Path):
    before = hashlib.sha256(PDF.read_bytes()).hexdigest()
    output = tmp_path / "timeline.html"
    report = tmp_path / "report.json"
    result = run_cli(str(PDF), "--output", str(output), "--report", str(report))
    assert result.returncode == 0, result.stderr
    assert hashlib.sha256(PDF.read_bytes()).hexdigest() == before
    html = output.read_text(encoding="utf-8")
    match = re.search(r"const DATA=(\{.*?\});", html, re.DOTALL)
    assert match
    data = json.loads(match.group(1))
    assert data["fiscalYearBE"] == 2570
    assert data["canvas"] == {"width": 1200, "height": 675}
    assert len(data["allMilestones"]) == 21
    assert len(data["milestones"]) == 16
    assert {m["group"] for m in data["allMilestones"]} == {
        "การทบทวนและวางแผนงบประมาณ", "การจัดทำงบประมาณ", "การอนุมัติงบประมาณ"
    }
    assert [m["startDate"] for m in data["milestones"]] == sorted(
        m["startDate"] for m in data["milestones"]
    )
    assert next(m for m in data["allMilestones"] if m["seq"] == 21)["startDate"] == "2026-12-03"
    assert next(m for m in data["allMilestones"] if m["seq"] == 21)["sourcePage"] == 3
    assert json.loads(report.read_text(encoding="utf-8"))["verified_source"] is True


def test_missing_and_non_pdf_inputs(tmp_path: Path):
    assert run_cli(str(tmp_path / "missing.pdf")).returncode == 2
    text_file = tmp_path / "not-pdf.txt"
    text_file.write_text("x")
    assert run_cli(str(text_file)).returncode == 2


def test_output_protection(tmp_path: Path):
    existing = tmp_path / "exists.html"
    existing.write_text("keep")
    result = run_cli(str(PDF), "--output", str(existing))
    assert result.returncode == 4
    assert existing.read_text() == "keep"
    assert run_cli(str(PDF), "--output", str(PDF)).returncode == 4
