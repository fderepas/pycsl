"""Test 1244 — ROUTE #90 ESCALATION: the lie crosses a call, from PyCSL source alone.

NOT TRUE OF THE PROGRAM. CPython: g(1) returns 0, so f() returns 0, not 1. MEASURED.

This is the witness that makes #90 severity-1 rather than a hypothetical about an
external caller: **PyCSL's own front-end accepts the int literal `1` as the actual for a
`bool` parameter**, so no appeal to a foreign caller is needed to reach the defect.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires x == 1
#@ ensures \result == 1
#@ assigns \nothing
def g(x: bool) -> int:
    if x is True:
        return 1
    return 0

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return g(1)
