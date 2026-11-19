r"""Test 2095 — gen #36 (expected FAIL): CONTROL — a record returned from inside a LOOP is
NOT in tail position of an if-tree, so the seam does not fire and the function keeps the
pre-existing `raise (Return <record>)` lowering, which Why3 rejects (fail-closed refusal).
The claim is true; the point is that the out-of-scope shape is still refused, never
mis-lowered.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class P:
    x: int
    y: int



#@ requires n >= 0
#@ ensures \result.x == 3
#@ assigns \nothing
def h(n: int) -> P:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        if i == 2:
            return P(3, i)
        i = i + 1
    return P(3, 0)
