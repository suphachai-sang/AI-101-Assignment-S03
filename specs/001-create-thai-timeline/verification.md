# Verification: HW03 timeline

**Date**: 2026-10-15

## Result

`python3 src/thai_timeline.py HW03-Input.pdf --output dist/hw03.html --force --report dist/report.json`
generated a self-contained HTML Canvas timeline. The source PDF has fiscal year
2570 and 21 numbered rows across three scanned pages. The canvas presents 16
selected milestones; `allMilestones` in the embedded JSON retains all 21 rows
with their PDF page numbers. The reference JPG has fiscal year 2569, so it was
used for visual layout only.

## Acceptance evidence

| Criterion | Evidence | Status |
|---|---|---|
| SC-001 | Canvas and Chrome preview both measure 1200×675 | Pass |
| SC-002 | Human-checked source fixture has per-row PDF page provenance; fixture applies only to exact SHA-256 | Pass for supplied PDF |
| SC-003 | `milestones` sorted by `startDate`, including shared start dates | Pass |
| SC-004 | Chrome headless screenshot inspected at actual size; labels and cards are visible without clipping | Pass for supplied PDF |
| SC-005 | Unknown PDF and unverified extraction stop before writing HTML; missing/non-PDF inputs and output collisions have distinct exit codes | Pass |
| SC-006 | 21 verified rows cover all three groups; notes are excluded; 16 selected for the canvas | Pass for supplied PDF |
| SC-007 | PDF title is fiscal year 2570; reference year 2569 is not copied into the output | Pass |
| SC-008 | Chrome screenshot inspected: all odd sequence numbers are above the axis and all even numbers below it | Pass |
| SC-009 | Chrome screenshot inspected: visible title, dates, month labels, and sequence numbers use Arabic digits; Sarabun Regular/Bold are embedded in the HTML | Pass |

## Commands

```bash
python3 -m pytest tests/ -q
git diff --check
```

The remaining open work in `tasks.md` is improving the generic OCR parser for
other scanned PDFs and writing the assignment's separate prompt-only comparison
and reflection. The supplied PDF output is complete without those steps.
