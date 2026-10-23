"""Test 1081 — ROUTE #49 negative witness (b): the callee could even declare
`assigns \\nothing` and nothing caught it.

FALSE OF THE PROGRAM: `f([0, 0])` returns 3 in Python.

1080's `g` at least DECLARED `assigns a`. This one declares `assigns \\nothing` while
appending to the parameter — a frame LIE — and the frame plane did not catch it either,
because the snapshot lowering genuinely writes nothing: the model and the declaration agree
with each other and both disagree with Python. That is the sharpest form of this defect and
the reason the repair belongs at the LOWERING rather than in the frame checker. At the
parent commit b7898d0e `\\result == 2` PROVED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires True
#@ ensures True
#@ assigns \nothing
def g(a: list) -> None:
    a.append(1)


#@ requires \length(a) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(a: list) -> int:
    g(a)
    return len(a)
