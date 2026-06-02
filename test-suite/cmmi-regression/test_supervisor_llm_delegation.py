"""Item 1.4c — mock-LLM end-to-end tests for agent-feature-supervisor.

Exercises the delegation path: prompt building, fenced-diff
extraction, `git apply` validation, and the per-phase rollback flow.
We import the supervisor module directly (rather than spawning a
subprocess) so we can monkey-patch `llm_generate` deterministically.

Per cmmi-tailoring-plan-follow-up-2.md Item 1.4c.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
# Add agents dir to path so the supervisor's `from llm_client import log`
# resolves to the real shared module.
sys.path.insert(0, str(REPO_ROOT / "src" / "pycsl" / "agents"))

# Dynamic import — the module file name has a `-` so we can't use
# the regular `import` keyword.
_SPEC = importlib.util.spec_from_file_location(
    "agent_feature_supervisor",
    REPO_ROOT / "src" / "pycsl" / "agents" / "agent-feature-supervisor.py",
)
assert _SPEC is not None and _SPEC.loader is not None
sup = importlib.util.module_from_spec(_SPEC)
# Dataclasses require the module to be in sys.modules before exec_module
sys.modules["agent_feature_supervisor"] = sup
_SPEC.loader.exec_module(sup)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# A canonical mock diff that adds a comment line to a tiny fixture file.
# Used by both the success-path and rollback-path tests; the rollback
# test additionally injects a gate-breaking second hunk.
MOCK_DIFF_GOOD = """diff --git a/proposed-features/.cmmi-llm-fixture.py b/proposed-features/.cmmi-llm-fixture.py
--- a/proposed-features/.cmmi-llm-fixture.py
+++ b/proposed-features/.cmmi-llm-fixture.py
@@ -1,2 +1,3 @@
 # cmmi-llm test fixture — DELETE after test runs.
 # Touched by test_supervisor_llm_delegation.
+# Added by mock LLM during 1.4c test.
"""


@pytest.fixture
def mock_repo_fixture():
    """A tiny tracked file under proposed-features/ that the diff can target.
    Cleans up regardless of test outcome.
    """
    p = REPO_ROOT / "proposed-features" / ".cmmi-llm-fixture.py"
    p.write_text(
        "# cmmi-llm test fixture — DELETE after test runs.\n"
        "# Touched by test_supervisor_llm_delegation.\n"
    )
    # Stage it so `git apply` works against the working tree
    subprocess.run(["git", "add", "-N", str(p.relative_to(REPO_ROOT))],
                   cwd=str(REPO_ROOT), capture_output=True)
    yield p
    # Cleanup
    if p.exists():
        p.unlink()
    subprocess.run(["git", "reset", "HEAD", "--", str(p.relative_to(REPO_ROOT))],
                   cwd=str(REPO_ROOT), capture_output=True)


# ---------------------------------------------------------------------------
# Unit tests — _extract_diff, _apply_diff, _build_phase_prompt
# ---------------------------------------------------------------------------

def test_extract_diff_finds_fenced_diff():
    llm_output = (
        "Some prose.\n\n"
        "```diff\n"
        "diff --git a/foo b/foo\n"
        "--- a/foo\n+++ b/foo\n"
        "@@ -1 +1,2 @@\n line\n+new\n"
        "```\n\n"
        "Trailing text."
    )
    diff = sup._extract_diff(llm_output)
    assert diff is not None
    assert diff.startswith("diff --git")
    assert "+new" in diff


def test_extract_diff_treats_refuse_as_no_diff():
    llm_output = (
        "I cannot do this.\n"
        "```diff\n"
        "# refuse: phase touches a load-bearing file I won't edit\n"
        "```\n"
    )
    assert sup._extract_diff(llm_output) is None


def test_extract_diff_missing_block_returns_none():
    assert sup._extract_diff("just prose, no diff block") is None


def test_apply_diff_validates_before_writing(mock_repo_fixture):
    # Apply succeeds against the fixture
    ok, err = sup._apply_diff(MOCK_DIFF_GOOD)
    assert ok, f"expected good diff to apply; got error: {err}"
    text = mock_repo_fixture.read_text()
    assert "Added by mock LLM" in text


def test_apply_diff_rejects_garbage():
    ok, err = sup._apply_diff("this is not a diff")
    assert not ok
    assert "git apply" in err.lower()


def test_build_phase_prompt_includes_target_contents(tmp_path):
    """The phase prompt inlines target file contents so the LLM has context."""
    target = tmp_path / "stub.py"
    target.write_text("def stub() -> int:\n    return 0\n")

    phase = sup.Phase(
        number=1,
        title="Test",
        target_files=[str(target.resolve())],  # absolute path resolves to itself
        raw_body="| File | Change |\n|---|---|\n| stub.py | rewrite |",
    )
    # The supervisor's path-stripping logic walks lstrip("./").lstrip("/")
    # then prepends _PROJECT_ROOT. An absolute path under tmp_path won't
    # resolve cleanly. Use a path RELATIVE to REPO_ROOT instead.
    rel = "proposed-features/.cmmi-llm-prompt-fixture.py"
    fixture = REPO_ROOT / rel
    fixture.write_text("def stub_v2() -> int:\n    return 1\n")
    try:
        phase2 = sup.Phase(
            number=1,
            title="Test phase",
            target_files=[rel],
            raw_body="raw body content",
        )
        prompt = sup._build_phase_prompt(phase2, "plan text irrelevant")
        assert "Test phase" in prompt
        assert "raw body content" in prompt
        assert "stub_v2" in prompt, (
            "prompt must inline the target file contents so the LLM "
            "has the current state to diff against"
        )
        assert "## This phase: Phase 1" in prompt
    finally:
        if fixture.exists():
            fixture.unlink()


# ---------------------------------------------------------------------------
# End-to-end — monkey-patched llm_generate
# ---------------------------------------------------------------------------

def test_delegate_phase_success(monkeypatch, mock_repo_fixture, tmp_path):
    """Happy path: mock LLM returns a good diff, apply succeeds, gate
    runs, no rollback."""
    # Patch llm_generate at the supervisor module level. The function
    # is imported INSIDE _delegate_phase via local import, so we have
    # to patch sys.modules so the local import sees our mock.
    from types import SimpleNamespace
    mock_module = SimpleNamespace(
        llm_generate=lambda **kwargs: f"Here is the diff:\n\n```diff\n{MOCK_DIFF_GOOD}\n```\n",
        log=lambda *a, **k: None,
    )
    monkeypatch.setitem(sys.modules, "llm_client", mock_module)

    # Also stub out run_gate so this test doesn't run the full CMMI gate
    # (which would invoke pytest recursively — infinite loop)
    monkeypatch.setattr(
        sup, "run_gate",
        lambda: [sup.GateResult("mock-gate", True, False, "")],
    )

    phase = sup.Phase(
        number=99,
        title="mock delegation",
        target_files=["proposed-features/.cmmi-llm-fixture.py"],
        raw_body="dummy",
    )
    ok, msg = sup._delegate_phase(phase, "plan text", "test-mock-delegation")
    assert ok, f"expected success; got msg={msg!r}"

    text = mock_repo_fixture.read_text()
    assert "Added by mock LLM" in text, "diff was not applied"

    # Audit-trail tag should remain
    tag = sup._phase_tag("test-mock-delegation", 99)
    r = subprocess.run(["git", "tag", "-l", tag],
                       cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert tag in r.stdout, "phase-start tag should remain on success (audit trail)"
    # Clean up tag now to keep the working tree tidy
    subprocess.run(["git", "tag", "-d", tag], cwd=str(REPO_ROOT),
                   capture_output=True)


def test_delegate_phase_rollback_on_gate_fail(monkeypatch, mock_repo_fixture):
    """Gate-fail path: diff applies, gate fails, rollback restores file."""
    from types import SimpleNamespace
    mock_module = SimpleNamespace(
        llm_generate=lambda **kwargs: f"```diff\n{MOCK_DIFF_GOOD}\n```",
        log=lambda *a, **k: None,
    )
    monkeypatch.setitem(sys.modules, "llm_client", mock_module)

    # Force the gate to fail
    monkeypatch.setattr(
        sup, "run_gate",
        lambda: [sup.GateResult("mock-gate", False, False, "synthetic failure")],
    )

    pre_text = mock_repo_fixture.read_text()

    phase = sup.Phase(
        number=42,
        title="rollback test",
        target_files=["proposed-features/.cmmi-llm-fixture.py"],
        raw_body="dummy",
    )
    ok, msg = sup._delegate_phase(phase, "plan text", "test-rollback")
    assert not ok
    assert "gate-fail" in msg.lower() or "rolled back" in msg.lower()

    # File should be back to pre-diff state.
    # Note: the fixture is created via `git add -N` (intent-to-add) so
    # rollback to the pre-phase tag may either (a) remove the file
    # entirely (it didn't exist in HEAD) or (b) restore the pre-diff
    # content. Both are correct rollback outcomes.
    if mock_repo_fixture.exists():
        post_text = mock_repo_fixture.read_text()
        assert post_text == pre_text, (
            f"rollback should restore fixture content; "
            f"pre={pre_text!r} post={post_text!r}"
        )
    # If the file is gone, rollback restored to pre-creation state — also OK.

    # Tag should be gone
    tag = sup._phase_tag("test-rollback", 42)
    r = subprocess.run(["git", "tag", "-l", tag],
                       cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert tag not in r.stdout, "rollback should delete the phase-start tag"


def test_delegate_phase_llm_refusal(monkeypatch, mock_repo_fixture):
    """LLM refuses → exit early with no diff applied, no tag survives."""
    from types import SimpleNamespace
    mock_module = SimpleNamespace(
        llm_generate=lambda **kwargs: "```diff\n# refuse: I won't do this\n```",
        log=lambda *a, **k: None,
    )
    monkeypatch.setitem(sys.modules, "llm_client", mock_module)

    pre_text = mock_repo_fixture.read_text()

    phase = sup.Phase(
        number=7,
        title="refusal test",
        target_files=["proposed-features/.cmmi-llm-fixture.py"],
        raw_body="dummy",
    )
    ok, msg = sup._delegate_phase(phase, "plan text", "test-refusal")
    assert not ok
    assert "refused" in msg.lower() or "no diff" in msg.lower()

    # File untouched
    assert mock_repo_fixture.read_text() == pre_text


# ---------------------------------------------------------------------------
# Safety — _git refuses forbidden args
# ---------------------------------------------------------------------------

def test_git_helper_refuses_forbidden_args():
    """_git must refuse --hard, push, commit, etc."""
    with pytest.raises(RuntimeError, match="forbidden"):
        sup._git("reset", "--hard")
    with pytest.raises(RuntimeError, match="forbidden"):
        sup._git("push", "origin", "main")
    with pytest.raises(RuntimeError, match="forbidden"):
        sup._git("commit", "-m", "foo")
    with pytest.raises(RuntimeError, match="forbidden"):
        sup._git("clean", "-fd")


# ---------------------------------------------------------------------------
# Rollback safety — pre-existing untracked targets must survive (data-loss fix)
# ---------------------------------------------------------------------------

def _cleanup_phase(slug, tag, paths):
    for p in paths:
        if p.exists():
            p.unlink()
    subprocess.run(["git", "tag", "-d", tag], cwd=str(REPO_ROOT), capture_output=True)
    shutil.rmtree(REPO_ROOT / "metrics" / "feature-supervisor" / slug, ignore_errors=True)


def test_rollback_restores_preexisting_untracked_target():
    """A pre-existing UNTRACKED phase target must survive a rollback.

    Regression: the per-phase tag only snapshots tracked state, so rollback used
    to delete untracked targets it couldn't find in the tag."""
    slug, phase_no = "test-untracked-rollback", 99
    rel = "proposed-features/.cmmi-untracked-rollback-fixture.py"
    p = REPO_ROOT / rel
    original = "# pre-existing untracked Phase target — must survive rollback\n"
    tag = sup._phase_tag(slug, phase_no)
    try:
        p.write_text(original)
        # phase start: tag HEAD, then snapshot untracked targets
        subprocess.run(["git", "tag", "-f", tag], cwd=str(REPO_ROOT), capture_output=True)
        sup._snapshot_untracked_targets(slug, phase_no, [rel])
        # delegate clobbers it
        p.write_text("# delegate clobbered this\n")
        assert sup._rollback_phase(slug, phase_no, [rel])
        assert p.exists(), "untracked target was deleted by rollback (regression)"
        assert p.read_text() == original, "untracked target not restored to original content"
    finally:
        _cleanup_phase(slug, tag, [p])


def test_rollback_still_deletes_delegate_created_file():
    """A target with no phase-start snapshot (genuinely delegate-created) is still removed."""
    slug, phase_no = "test-created-rollback", 98
    rel = "proposed-features/.cmmi-created-rollback-fixture.py"
    p = REPO_ROOT / rel
    tag = sup._phase_tag(slug, phase_no)
    try:
        subprocess.run(["git", "tag", "-f", tag], cwd=str(REPO_ROOT), capture_output=True)
        # snapshot runs while the file does NOT yet exist → nothing snapshotted
        sup._snapshot_untracked_targets(slug, phase_no, [rel])
        p.write_text("# created by the delegate\n")  # delegate creates it afterwards
        assert sup._rollback_phase(slug, phase_no, [rel])
        assert not p.exists(), "delegate-created file should be removed on rollback"
    finally:
        _cleanup_phase(slug, tag, [p])
