"""The checked transcription must never be applied to a different PDF."""
from pathlib import Path

from timeline.sample_data import load_verified_sample


def test_verified_fixture_is_bound_to_pdf_bytes(tmp_path: Path):
    pdf = Path(__file__).resolve().parents[2] / "HW03-Input.pdf"
    verified = load_verified_sample(pdf)
    assert verified is not None
    document, featured = verified
    assert document.fiscal_year_be == 2570
    assert len(document.all_milestones()) == 21
    assert len(featured) == 16

    changed = tmp_path / "changed.pdf"
    changed.write_bytes(pdf.read_bytes() + b"\n")
    assert load_verified_sample(changed) is None
