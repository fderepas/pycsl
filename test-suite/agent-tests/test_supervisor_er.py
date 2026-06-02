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


def _load_supervisor_module():
    """Dynamically import the hyphen-named supervisor as a module.
    Used by the gap-4 delegation-acceptance unit test.

    Registers in sys.modules so dataclass introspection
    (which walks `sys.modules[cls.__module__]`) succeeds for the
    dynamically-instantiated Phase / AcceptanceClaim objects below.
    """
    import sys, importlib.util as u
    name = "agent_feature_supervisor_under_test"
    if name in sys.modules:
        return sys.modules[name]
    spec = u.spec_from_file_location(
        name,
        REPO_ROOT / "src" / "pycsl" / "agents" / "agent-feature-supervisor.py")
    m = u.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def test_delegation_runs_acceptance_post_gate(monkeypatch):
    """Gap 4: `_delegate_phase` evaluates phase acceptance after the
    gate passes — and triggers rollback if a claim fails.

    Mocks: llm_client.llm_generate (returns a dummy diff), _apply_diff
    (no-op success), run_gate (no failures), _rollback_phase (record
    invocations). The acceptance executor itself runs against real
    `true` / `false` claims (no mocking needed there)."""
    afs = _load_supervisor_module()

    # Stub the llm_client import _delegate_phase performs at runtime.
    import sys
    fake_module = type(sys)("llm_client")
    fake_module.llm_generate = lambda **kw: "```diff\n# noop diff\n```"
    monkeypatch.setitem(sys.modules, "llm_client", fake_module)

    # Stub the filesystem-changing helpers
    monkeypatch.setattr(afs, "_apply_diff", lambda diff: (True, ""))
    monkeypatch.setattr(afs, "run_gate", lambda: [])
    rollback_calls = []
    monkeypatch.setattr(
        afs, "_rollback_phase",
        lambda slug, n, targets: (
            rollback_calls.append((slug, n, list(targets))), True)[1])

    # Stub git-tag creation — `_delegate_phase` invokes
    # `subprocess.run(["git", "tag", "-f", tag], ...)` directly,
    # not via _git. We let it actually create the tag (cheap), then
    # clean up after the test.
    import subprocess
    orig_run = subprocess.run
    git_tags_created = []
    def fake_run(args, **kw):
        if isinstance(args, list) and args[:2] == ["git", "tag"]:
            git_tags_created.append(args[3] if len(args) > 3 else args[-1])
            return subprocess.CompletedProcess(args, 0, "", "")
        return orig_run(args, **kw)
    monkeypatch.setattr(subprocess, "run", fake_run)

    # Case 1: acceptance passes → delegation succeeds, no rollback
    pass_phase = afs.Phase(
        number=1, title="pass-case", target_files=[],
        acceptance=[afs.AcceptanceClaim(
            command="true",
            predicate=afs.ExitsN(kind="exits", n=0),
            raw_line="- `true` exits 0")],
    )
    ok, msg = afs._delegate_phase(pass_phase, "(plan body)", "er-test-slug")
    assert ok is True, f"expected delegation OK, got msg: {msg!r}"
    assert not rollback_calls, f"unexpected rollback: {rollback_calls}"

    # Case 2: acceptance fails → delegation reports fail, rollback fires
    fail_phase = afs.Phase(
        number=2, title="fail-case", target_files=["dummy.py"],
        acceptance=[afs.AcceptanceClaim(
            command="false",
            predicate=afs.ExitsN(kind="exits", n=0),
            raw_line="- `false` exits 0")],
    )
    ok, msg = afs._delegate_phase(fail_phase, "(plan body)", "er-test-slug")
    assert ok is False
    assert "acceptance-fail" in msg, f"expected acceptance-fail in msg, got: {msg!r}"
    assert len(rollback_calls) == 1
    assert rollback_calls[0][1] == 2   # phase number

    # Case 3: phase has NO acceptance — delegation should still succeed
    # (no claims to fail). This guards against a regression where the
    # acceptance loop accidentally throws on an empty list.
    rollback_calls.clear()
    bare_phase = afs.Phase(
        number=3, title="no-claims", target_files=[], acceptance=[],
    )
    ok, msg = afs._delegate_phase(bare_phase, "(plan body)", "er-test-slug")
    assert ok is True, f"expected OK for no-acceptance phase, got: {msg!r}"
    assert not rollback_calls


def test_status_in_prose_is_not_done():
    """Gap 5: prose mentions of `**Status:** DONE` in backticks /
    table cells must NOT cause the phase to be flagged DONE. If the
    regex anchor regresses, the failing acceptance would be masked
    as LEGACY_ACCEPTED and the supervisor would exit 0 — silently
    accepting a broken claim. The fixture has a `false` acceptance,
    so a correctly-functioning parser halts with exit 75."""
    r = _run("status-in-prose")
    assert r.returncode == EXIT_HUMAN_NEEDED, (
        "supervisor accepted a phase with prose-only Status mention "
        "— the line-anchor regex may have regressed.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    # Sanity: confirm the parser did NOT print LEGACY_ACCEPTED for
    # this phase (which would prove the false-positive).
    assert "LEGACY_ACCEPTED" not in r.stdout


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


def test_exits_failure_surfaces_stdout():
    """An `exits N` acceptance failure must include STDOUT in the reason.

    pycsl (and most tools) print the real failure to stdout while stderr
    carries only warnings; surfacing stderr alone hid the true cause of
    `exits` failures (e.g. the os.path `join` arity error in path_demo.py)."""
    afs = _load_supervisor_module()
    claim = afs.AcceptanceClaim(
        command="python3 -c \"print('PYCSL_STDOUT_MARKER') or exit(1)\"",
        predicate=afs.ExitsN(kind="exits", n=0),
        raw_line="- `python3 -c ...` exits 0",
    )
    res = afs._check_acceptance(claim, afs._PROJECT_ROOT, 30)
    assert res.passed is False
    assert "PYCSL_STDOUT_MARKER" in res.reason_if_failed, res.reason_if_failed
    assert "stdout" in res.reason_if_failed.lower()
