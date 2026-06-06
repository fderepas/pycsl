"""Layer D — behavioral-subtyping (Liskov) checks for overriding methods.

Exercises both directions of `--check-behavioral-subtyping`:
  * 0444 — a valid refinement (weaker precondition, stronger postcondition)
    must verify.
  * 0445 — a contravariant override (strengthened precondition) must be
    rejected with a non-zero exit.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PYCSL = REPO / "src" / "pycsl" / "pycsl.py"
CORPUS = REPO / "test-suite" / "corpus" / "pycsl-reference"


def _run(name: str) -> int:
    return subprocess.run(
        [sys.executable, str(PYCSL), "--check-behavioral-subtyping",
         str(CORPUS / name)],
        capture_output=True, text=True, cwd=str(REPO),
    ).returncode


def test_valid_override_passes():
    assert _run("0444.py") == 0


def test_contravariant_override_rejected():
    assert _run("0445.py") == 1
