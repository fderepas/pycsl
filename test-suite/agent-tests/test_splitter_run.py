"""Characterization (golden-master) test for agent-splitter's run_splitter.

run_splitter is a large orchestrator with subprocess/LLM/file-IO side effects.
This test mocks the side-effecting collaborators (all defined in the entry
module) and drives the *real* orchestration on a sample, pinning the observable
behaviour so the function can be decomposed safely:

  * every annotatable function is sent to the writer exactly once,
  * in bottom-up call-graph order (callees before callers),
  * a writer failure falls back (no crash) and the function still appears,
  * the reassembled result is returned.
"""
import importlib.util as iu
import re
import sys
from pathlib import Path

import pytest

_AGENTS = Path(__file__).resolve().parents[2] / "src" / "pycsl" / "agents"
sys.path.insert(0, str(_AGENTS))


def _load():
    spec = iu.spec_from_file_location(
        "agent_splitter_entry_under_test", _AGENTS / "agent-splitter.py")
    m = iu.module_from_spec(spec)
    sys.modules["agent_splitter_entry_under_test"] = m
    spec.loader.exec_module(m)
    return m


SAMPLE = '''def leaf(x: int) -> int:
    return x

def mid(x: int) -> int:
    return leaf(x)

def top(x: int) -> int:
    return mid(x)

def w(x: int) -> int:
    return xx(x)

def xx(x: int) -> int:
    return yy(x)

def yy(x: int) -> int:
    return zz(x)

def zz(x: int) -> int:
    return w(x)
'''


def _common_mocks(monkeypatch, m, writer_calls, *, writer_raises=False):
    def fake_writer(**kw):
        src = kw["function_source"]
        for nm in re.findall(r'^\s*def\s+(\w+)', src, re.M):
            writer_calls.append(nm)
        if writer_raises:
            raise RuntimeError("simulated writer failure")
        return src  # unchanged → body-preserved, no contracts
    monkeypatch.setattr(m, "_invoke_writer", fake_writer)
    monkeypatch.setattr(m, "_validate_pycsl_syntax", lambda *a, **k: True)
    monkeypatch.setattr(m, "_generate_class_invariants", lambda *a, **k: {})
    monkeypatch.setattr(m, "_generate_module_brief", lambda *a, **k: "")
    monkeypatch.setattr(m, "_lookup_catalog_seed", lambda *a, **k: None)
    monkeypatch.setattr(m, "_lookup_formal_model_hint", lambda *a, **k: None)
    monkeypatch.setattr(m, "_checkpoint_save", lambda *a, **k: None)
    monkeypatch.setattr(m, "_checkpoint_load", lambda *a, **k: None)
    monkeypatch.setattr(m, "log", lambda *a, **k: None)
    # Final full-file validation shells out to pycsl — stub it.
    import subprocess
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0] if a else [], 0, "", ""))


def _run(m, tmp_path):
    inp = tmp_path / "in.py"; inp.write_text(SAMPLE)
    return m.run_splitter(
        input_path=inp, output_path=tmp_path / "out.py",
        config_path=tmp_path / "cfg.json", project_root=tmp_path,
        project_directory=str(tmp_path))


def test_every_function_annotated_in_bottom_up_order(tmp_path, monkeypatch):
    m = _load()
    calls = []
    _common_mocks(monkeypatch, m, calls)
    result = _run(m, tmp_path)
    assert isinstance(result, str) and result.strip()
    assert set(calls) == {"leaf", "mid", "top", "w", "xx", "yy", "zz"}
    # callees precede callers along the linear chain
    assert calls.index("leaf") < calls.index("mid") < calls.index("top")


def test_writer_failure_falls_back_without_crashing(tmp_path, monkeypatch):
    m = _load()
    calls = []
    _common_mocks(monkeypatch, m, calls, writer_raises=True)
    result = _run(m, tmp_path)  # must not raise
    assert isinstance(result, str) and result.strip()
    assert calls  # writer was attempted


def test_validation_failure_triggers_one_retry(tmp_path, monkeypatch):
    """First validation fails, retry passes → the writer is invoked a second
    time for that function (the repair attempt)."""
    m = _load()
    calls = []
    _common_mocks(monkeypatch, m, calls)
    seen = {}

    def flaky_validate(annotated, *a, **k):
        # Identify the function by its def name; fail the first check, pass next.
        names = re.findall(r'^\s*def\s+(\w+)', annotated, re.M)
        key = names[0] if names else "?"
        seen[key] = seen.get(key, 0) + 1
        return seen[key] >= 2  # fail first, pass on retry
    monkeypatch.setattr(m, "_validate_pycsl_syntax", flaky_validate)

    result = _run(m, tmp_path)
    assert isinstance(result, str) and result.strip()
    # 'leaf' is a single-function SCC → first validate fails, retry → 2 writer calls
    assert calls.count("leaf") == 2, f"expected one retry for leaf, calls={calls}"


def test_body_not_preserved_path_does_not_crash(tmp_path, monkeypatch):
    """Writer returns a body-modified annotation → graft-or-fallback path runs;
    the function still appears in the result and nothing crashes."""
    m = _load()
    calls = []

    def mutating_writer(**kw):
        src = kw["function_source"]
        for nm in re.findall(r'^\s*def\s+(\w+)', src, re.M):
            calls.append(nm)
        # Add a contract line AND change the body (return x -> return 0).
        body_changed = re.sub(r'return x\b', 'return 0', src)
        return "    #@ ensures \\result >= 0\n" + body_changed
    monkeypatch.setattr(m, "_invoke_writer", mutating_writer)
    monkeypatch.setattr(m, "_validate_pycsl_syntax", lambda *a, **k: True)
    monkeypatch.setattr(m, "_generate_class_invariants", lambda *a, **k: {})
    monkeypatch.setattr(m, "_generate_module_brief", lambda *a, **k: "")
    monkeypatch.setattr(m, "_lookup_catalog_seed", lambda *a, **k: None)
    monkeypatch.setattr(m, "_lookup_formal_model_hint", lambda *a, **k: None)
    monkeypatch.setattr(m, "_checkpoint_save", lambda *a, **k: None)
    monkeypatch.setattr(m, "_checkpoint_load", lambda *a, **k: None)
    monkeypatch.setattr(m, "log", lambda *a, **k: None)
    import subprocess
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0] if a else [], 0, "", ""))

    result = _run(m, tmp_path)
    assert isinstance(result, str) and "def leaf" in result and calls
