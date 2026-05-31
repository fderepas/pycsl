"""Phase D check 7 — itertools.cycle 13:47:22 incident regression test.

Snapshot-replay (NOT live-replay). The 13:47:22 incident is frozen as
test-suite/cmmi-regression/fixtures/itertools-incident-snapshot.py;
this test exercises the DETERMINISTIC parts of the pipeline (the
regex classifier in agent-stdlib-annotate --detect-gaps and the
template fill in --propose-feature) — not the LLM that originally
produced the cite:_note text.

Acceptance criterion (per cmmi-tailoring-plan-follow-up.md Item 2):
   1. --detect-gaps against the fixture classifies `cycle` as
      iterator-semantics.
   2. --propose-feature iterator-semantics --proposal-threshold 1
      writes proposed-features/missing-iterator-semantics-feature.md.

If this test ever fails: agents have regressed and no longer spot
what the human spotted on 2026-05-31. That is the bug the whole
better-agent.md / cmmi-tailoring-plan stack exists to prevent.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (
    REPO_ROOT
    / "test-suite"
    / "cmmi-regression"
    / "fixtures"
    / "itertools-incident-snapshot.py"
)
ANNOTATE = REPO_ROOT / "bin" / "agent-stdlib-annotate"
GAP_REPORT = REPO_ROOT / "metrics" / "stdlib-gap-report.json"
PROPOSED = (
    REPO_ROOT / "proposed-features" / "missing-iterator-semantics-feature.md"
)


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Save & restore the live gap-report and proposed-features draft."""
    saved_report = GAP_REPORT.read_bytes() if GAP_REPORT.is_file() else None
    saved_proposal = PROPOSED.read_bytes() if PROPOSED.is_file() else None
    yield
    if saved_report is None:
        if GAP_REPORT.is_file():
            GAP_REPORT.unlink()
    else:
        GAP_REPORT.write_bytes(saved_report)
    if saved_proposal is None:
        if PROPOSED.is_file():
            PROPOSED.unlink()
    else:
        PROPOSED.write_bytes(saved_proposal)


def test_fixture_exists() -> None:
    """The 13:47:22 snapshot is the input the rest of this test consumes."""
    assert FIXTURE.is_file(), (
        f"Fixture missing: {FIXTURE}. The 13:47:22 incident snapshot is the "
        "canonical regression input — re-create it from missing-iter-feature.md "
        "if it has been deleted."
    )
    text = FIXTURE.read_text()
    # Sanity: the fixture must contain the cite:_note line that triggered
    # the original incident.
    assert "iterator-sequence semantics" in text
    assert "def cycle" in text


def test_detect_gaps_classifies_cycle_as_iterator_semantics() -> None:
    """Item 1.1 acceptance: the deterministic classifier recognises cycle."""
    r = _run([str(ANNOTATE), "--detect-gaps", "--scan-path", str(FIXTURE)])
    assert r.returncode == 0, (
        f"--detect-gaps failed: stdout=\n{r.stdout}\n\nstderr=\n{r.stderr}"
    )
    assert GAP_REPORT.is_file(), (
        f"Detector did not write {GAP_REPORT.relative_to(REPO_ROOT)}"
    )
    report = json.loads(GAP_REPORT.read_text())
    cats = report.get("categories", {})
    assert "iterator-semantics" in cats, (
        f"`iterator-semantics` category missing. Found: {sorted(cats)}"
    )
    iter_bucket = cats["iterator-semantics"]
    assert iter_bucket["count"] >= 1
    quals = [e["qualname"] for e in iter_bucket["examples"]]
    assert "cycle" in quals, (
        f"`cycle` not in iterator-semantics examples; got {quals}. "
        "The forward-scanning def-attribution in _scan_existing_notes has "
        "regressed (the cite:_note PRECEDES the def cycle line)."
    )


def test_propose_feature_emits_iterator_draft() -> None:
    """Item 1.2 acceptance: --propose-feature fills the template."""
    # First populate the gap report (depends on test ordering — use
    # explicit setup rather than relying on pytest order).
    r = _run([str(ANNOTATE), "--detect-gaps", "--scan-path", str(FIXTURE)])
    assert r.returncode == 0

    r = _run([
        str(ANNOTATE),
        "--propose-feature", "iterator-semantics",
        "--proposal-threshold", "1",
    ])
    assert r.returncode == 0, (
        f"--propose-feature failed: stdout=\n{r.stdout}\n\nstderr=\n{r.stderr}"
    )
    assert PROPOSED.is_file(), (
        f"Draft not created at {PROPOSED.relative_to(REPO_ROOT)}"
    )
    draft = PROPOSED.read_text()
    # Structural assertions — does the draft mirror missing-iter-feature.md?
    assert "STATUS: DRAFT" in draft, "draft missing STATUS: DRAFT header"
    assert "## The gap" in draft, "draft missing 'The gap' section"
    assert "## Scope" in draft, "draft missing 'Scope' section"
    assert "## Implementation surface" in draft, (
        "draft missing 'Implementation surface' section — supervisor cannot "
        "parse it without this section"
    )
    # Anchor function should be cycle (most-cited stuck function from fixture)
    assert "cycle" in draft.splitlines()[3] or "`cycle`" in draft[:1000], (
        "anchor function should be `cycle` — the only iterator-semantics "
        "function in the fixture"
    )


def test_supervisor_halts_on_load_bearing_files_in_human_drafted_plan() -> None:
    """Item 1.3 acceptance: supervisor exits 75 on the human-authored plan.

    Note: we test against the HUMAN-AUTHORED missing-iter-feature.md, not the
    auto-generated draft (which is a stub without a real Implementation
    surface). The supervisor must always halt at load-bearing files.
    """
    plan = REPO_ROOT / "missing-iter-feature.md"
    if not plan.is_file():
        pytest.skip(
            "missing-iter-feature.md not at repo root; supervisor test "
            "needs a real feature plan to parse."
        )
    r = _run([
        str(REPO_ROOT / "bin" / "agent-feature-supervisor"),
        "--feature-file", str(plan),
        "--skip-gate",
    ])
    assert r.returncode == 75, (
        f"Supervisor expected exit 75 (EXIT_HUMAN_NEEDED) on "
        f"missing-iter-feature.md; got {r.returncode}. "
        f"stdout=\n{r.stdout}\n\nstderr=\n{r.stderr}"
    )
    # Confirm a halt-report was written
    halt = (
        REPO_ROOT / "metrics" / "feature-supervisor"
        / "missing-iter-feature" / "halt-report.md"
    )
    assert halt.is_file(), f"Halt-report missing at {halt}"
    halt_text = halt.read_text()
    assert "Module2_Parser.py" in halt_text or "Module4_SemanticAnalyzer.py" in halt_text
    assert "LOAD-BEARING" in halt_text
