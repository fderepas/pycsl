"""Test 0846 — WL-03b regression lock (NEGATIVE twin of 0845). # pycsl-expected: FAIL

Guards the WL-03b fix from regressing to the unsound int collapse. `trunc_slot` reads a
`float` tuple slot holding `2.5` but claims `\result == 2.0` — the int-TRUNCATION value.
Under the (now-fixed) int collapse the field was `int` and `2.5` truncated to `2`, so
this would have PROVEN; under the faithful `real` model it is a false real claim
(`2.5 <> 2.0`) and MUST stay UNPROVEN.

If this test ever PASSES, the float field slot is being truncated to int again (the
unsound collapse re-appeared).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Tuple
from dataclasses import dataclass


@dataclass
class P:
    n: int
    f: float


#@ requires t[1] == 2.5
#@ ensures \result == 2.0
def trunc_slot(t: Tuple[int, float]) -> float:
    """Returns 2.5 but claims == 2.0 — false unless the real slot is truncated to int."""
    return t[1]


#@ requires q.f == 2.5
#@ ensures \result == 2.0
def trunc_field(q: P) -> float:
    """Returns 2.5 but claims == 2.0 — false unless the real field is truncated to int."""
    return q.f


if __name__ == "__main__":
    assert trunc_slot((1, 2.5)) == 2.5   # real value is 2.5, contract claims 2.0 — FALSE
    assert trunc_field(P(0, 2.5)) == 2.5
