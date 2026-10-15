"""Environment readiness checks for integration tests (T003)."""
import shutil
import subprocess
import sys

import pytest


def _tesseract_has_thai() -> bool:
    exe = shutil.which("tesseract")
    if not exe:
        return False
    try:
        out = subprocess.run(
            [exe, "--list-langs"], capture_output=True, text=True, timeout=15
        )
        return "Thai" in out.stdout or "tha" in out.stdout
    except Exception:
        return False


def _has_pymupdf() -> bool:
    try:
        import fitz  # noqa: F401

        return True
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    reasons = []
    if sys.version_info < (3, 11):
        reasons.append("Python 3.11 or newer required")
    if not _tesseract_has_thai():
        reasons.append("Tesseract with Thai language data not available")
    if not _has_pymupdf():
        reasons.append("PyMuPDF not available")
    if reasons:
        skip = pytest.mark.skip(reason="; ".join(reasons))
        for item in items:
            item.add_marker(skip)
