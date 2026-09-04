"""Test 1026 — ROUTE #36, the variant that refutes the obvious narrowing.

FALSE OF THE PROGRAM: same as 1025 and Python returns 2, but here `i` is NOT
assigned before the loop.

This file exists because the first guess at a narrow fix was "only refuse when
the loop target is ASSIGNED before the loop, so there is a stale value to
expose". That is wrong: Module 6 declares the loop target as an OUTER ref
whether or not the source pre-assigns it, so the leak needs no stale value and
this proved `\result == 0` at c4233fed exactly like 1025.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    #@ loop invariant 0 <= i and i <= 3
    #@ loop variant 3 - i
    for i in range(3):
        pass
    return i
