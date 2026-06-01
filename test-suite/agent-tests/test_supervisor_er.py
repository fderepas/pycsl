"""Pytest harness for agent-feature-supervisor's Extreme Rigor mode.

Each test invokes `bin/agent-feature-supervisor --feature-file <fixture>
--skip-gate` against one of the er-fixtures/*.md plans and asserts the
exit code and (where relevant) the halt-report contents.

The fixtures are deliberately tiny — they exercise the ER acceptance
mechanism, not the rest of the supervisor.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "test-suite" / "agent-tests" / "er-fixtures"
SUPERVISOR = REPO_ROOT / "bin" / "agent-feature-supervisor"
HALT_DIR = REPO_ROOT / "metrics" / "feature-supervisor"

EXIT_OK = 0
EXIT_HUMAN_NEEDED = 75


def _run(fixture_name: str) -> subprocess.CompletedProcess:
    fixture = FIXTURE_DIR / f"{fixture_name}.md"
    assert fixture.is_file(), f"fixture missing: {fixture}"
    return subprocess.run(
        [str(SUPERVISOR), "--feature-file", str(fixture), "--skip-gate"],
        cwd=str(REPO_ROOT),
        capture_output=True, text=True, timeout=120,
    )


def _halt_report(fixture_stem: str) -> str:
    """Read the halt-report for a fixture. Returns '' if no report
    exists (i.e., the supervisor exited OK without halting)."""
    path = HALT_DIR / fixture_stem / "halt-report.md"
    return path.read_text() if path.is_file() else ""


def test_minimal_pass_exits_ok():
    r = _run("minimal-pass")
    assert r.returncode == EXIT_OK, f"stdout: {r.stdout}\nstderr: {r.stderr}"


def test_minimal_fail_halts_with_acceptance_failed():
    r = _run("minimal-fail")
    assert r.returncode == EXIT_HUMAN_NEEDED
    report = _halt_report("minimal-fail")
    assert "ACCEPTANCE_FAILED" in report
    assert "false" in report   # the failing claim's command


def test_forged_status_halts_with_status_forged():
    r = _run("forged-status")
    assert r.returncode == EXIT_HUMAN_NEEDED
    report = _halt_report("forged-status")
    assert "STATUS_FORGED" in report


def test_legacy_done_grandfathered():
    """DONE phase without Acceptance block should not halt."""
    r = _run("legacy-done")
    assert r.returncode == EXIT_OK
    # The LEGACY_ACCEPTED informational line should be in the run log.
    assert "LEGACY_ACCEPTED" in r.stdout


def test_missing_acceptance_halts():
    r = _run("missing-acceptance")
    assert r.returncode == EXIT_HUMAN_NEEDED
    report = _halt_report("missing-acceptance")
    assert "MISSING_ACCEPTANCE" in report


def test_explicit_none_opts_out():
    r = _run("explicit-none")
    assert r.returncode == EXIT_OK
    assert "OPTOUT" in r.stdout or "opted out" in r.stdout


def test_forbidden_rm_halts_with_claim_rejected():
    r = _run("forbidden-rm")
    assert r.returncode == EXIT_HUMAN_NEEDED
    report = _halt_report("forbidden-rm")
    assert "CLAIM_REJECTED" in report


def test_forbidden_redirect_halts_with_claim_rejected():
    """Gap 7: extended safety classifier rejects output-redirect."""
    r = _run("forbidden-redirect")
    assert r.returncode == EXIT_HUMAN_NEEDED
    report = _halt_report("forbidden-redirect")
    assert "CLAIM_REJECTED" in report
    assert "output redirect" in report or "forbidden" in report


def test_every_fixture_has_acceptance_or_status():
    """ER eats its own dogfood: every fixture itself must declare
    Acceptance (open) or Status: DONE (legacy) — EXCEPT the
    negative-test fixtures whose purpose is to demonstrate the
    missing/forbidden cases.
    """
    NEGATIVE_FIXTURES = {"missing-acceptance.md"}
    for fixture in FIXTURE_DIR.glob("*.md"):
        if fixture.name in NEGATIVE_FIXTURES:
            continue
        text = fixture.read_text()
        has_acceptance = "**Acceptance:**" in text
        has_status_done = "**Status:** DONE" in text
        assert has_acceptance or has_status_done, (
            f"{fixture.name}: fixture lacks both Acceptance and Status — "
            f"ER applies recursively to its own test fixtures"
        )
