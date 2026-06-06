"""Test 0564 — contract-reference ordering (scc.md).

`caller`'s contract references the pure function `helper`, `caller` is defined
BEFORE `helper` in source, and `caller` has NO body call to it — so only the
*contract* reference forces `helper` to be emitted first. Without the contract-
reference edge in the SCC call graph (scc.md), `caller` emits before `helper` and
Why3 reports `unbound function or predicate symbol 'helper'`. With the edge,
`helper` is ordered first and the file verifies.

This is the regression twin: it proves the EDGE — not source-order luck — does the
work, and stops a future refactor from silently reverting to body-only edges.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires helper() >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def caller(x: int) -> int:
    return x if x >= 0 else 0


#@ ensures \result == 0
#@ assigns \nothing
def helper() -> int:
    return 0
