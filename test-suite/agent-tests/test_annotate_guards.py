"""Regression net for the extracted agent-annotate guard library.

`agent-annotate.py` was modularized: its ~48 `code: str -> str` guard
transforms now live in `agent_annotate/guards.py`, re-exported into the entry
script. There were no tests before the split; this is the net that was built
to verify it (and guards against future wiring/regression breakage).

The checks are deliberately behavioral (each guard is actually *called*) —
`py_compile` cannot catch a missing-import `NameError` inside a guard body.
"""
import inspect
import sys
from pathlib import Path

import pytest

_AGENTS = Path(__file__).resolve().parents[2] / "src" / "pycsl" / "agents"
sys.path.insert(0, str(_AGENTS))

from agent_annotate import guards  # noqa: E402

# A reasonably rich sample so guards have something to match (contracts, loop
# invariant, list/str params, division, a while-return shape).
SAMPLE = '''#@ requires n >= 0
def f(n: int, arr: list, s: str) -> int:
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    for i in range(n):
        x = arr[i]
    return n
'''


def _single_arg_guards():
    out = []
    for name, fn in inspect.getmembers(guards, inspect.isfunction):
        if fn.__module__ != "agent_annotate.guards":
            continue
        req = [p for p in inspect.signature(fn).parameters.values()
               if p.default is inspect._empty
               and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        if len(req) == 1:
            out.append((name, fn))
    return out


@pytest.mark.parametrize("name,fn", _single_arg_guards(),
                         ids=lambda v: v if isinstance(v, str) else "")
def test_single_arg_guard_runs(name, fn):
    """Every single-argument guard runs on the sample without error and
    returns a str (a transform) or a callable (a closure-factory guard)."""
    # The call itself is the test (catches missing-import NameErrors and other
    # crashes). Return shapes in this library: str (transform), bool (a
    # predicate helper like `_preceding_has_trusted`), or callable (a
    # closure-factory guard).
    res = fn(SAMPLE)
    assert isinstance(res, (str, bool)) or callable(res), (
        f"{name} returned {type(res).__name__}")


def test_closure_factory_guard_works():
    """`_guard_body_preservation` returns a working transform."""
    transform = guards._guard_body_preservation(SAMPLE)
    assert callable(transform)
    assert isinstance(transform(SAMPLE), str)


def test_guard_library_populated():
    n = sum(1 for _, fn in inspect.getmembers(guards, inspect.isfunction)
            if fn.__module__ == "agent_annotate.guards")
    assert n >= 40, f"expected the full guard library, found only {n}"
