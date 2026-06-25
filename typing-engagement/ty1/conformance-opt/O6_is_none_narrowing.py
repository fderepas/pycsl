"""Static gate O6 — `is None` narrowing (the load-bearing Optional clause).

Spec clause O6 (optional-twoplane-spec.md §1.2): after `if x is None:`
where `x: Optional[X]`, on the True branch `x` has type `None`; on the
False branch `x` has type `X` (there is no residual union — Optional has
exactly two arms). The False branch uses `x` as an `int`, so the
narrowing must discharge the int-operator obligation on `x`.

NOTE: per the engagement instructions, the postcondition is `ensures True`
(NOT `ensures \\result >= 0`); the latter is a separate postcondition
issue tracked as GAP-001b on the Union side, NOT an Optional lowering
gap. The O6 witness checks ONLY the narrowing lowering.

Expected (from spec): prove (narrowing VC on the False branch).
"""

from typing import Optional


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(x: Optional[int]) -> int:
    if x is None:
        return 0
    return x


if __name__ == "__main__":
    assert f(1) == 1
    assert f(None) == 0
    print("PASS")
