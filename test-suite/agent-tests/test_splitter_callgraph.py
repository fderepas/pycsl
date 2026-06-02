"""Regression net for the extracted agent-splitter call-graph subsystem.

`agent-splitter.py` was modularized: its pure AST analysis (call-graph build +
Tarjan SCC) now lives in `agent_splitter/callgraph.py`, re-exported into the
entry script. There were no tests before the split; this locks in the
call-graph / strongly-connected-component behavior that the bottom-up
annotation order depends on.
"""
import sys
from pathlib import Path

_AGENTS = Path(__file__).resolve().parents[2] / "src" / "pycsl" / "agents"
sys.path.insert(0, str(_AGENTS))

from agent_splitter import callgraph as cg  # noqa: E402

SRC = '''def fact(n: int) -> int:
    if n <= 1:
        return 1
    return n * fact(n - 1)

def is_even(n: int) -> int:
    return is_odd(n - 1)

def is_odd(n: int) -> int:
    return is_even(n - 1)

class Bank:
    def deposit(self, x: int) -> int:
        return self.balance(x)
    def balance(self, x: int) -> int:
        return x
'''


def _analyze():
    funcs, fmap = cg._extract_functions(SRC)
    cg._build_call_graph(funcs, fmap)
    scc = [sorted(c) for c in cg._tarjan_scc(fmap)]
    return scc, sorted(fmap)


def test_qualified_names():
    _, names = _analyze()
    assert names == ["Bank.balance", "Bank.deposit", "fact", "is_even", "is_odd"]


def test_mutual_recursion_is_one_scc():
    scc, _ = _analyze()
    assert ["is_even", "is_odd"] in scc, f"expected mutual-recursion SCC, got {scc}"


def test_self_recursion_is_singleton_scc():
    scc, _ = _analyze()
    assert ["fact"] in scc
