"""Static gate L2 — narrowing by equality (the load-bearing Literal narrowing).

Spec clause L2 (literal-twoplane-spec.md §1.2): after `if x == 1:` where
`x: Literal[1, 2]`, the True branch narrows to `Literal[1]` (path condition
`x = 1`) and the False branch narrows to `Literal[2]` (the residual
disjunct, since `x = 1` is ruled out and the precondition's
`x = 1 \/ x = 2` leaves only `x = 2`). Both branches return a distinct
int (0 on True, 1 on False); the postcondition `\result >= 0` discharges
on both paths.

The narrowing is emergent from the standard path-condition VC on the
existing `if x == v` lowering — no new IR node.

Expected (from spec): PASS (narrowing VCs discharge on both branches).
"""

from typing import Literal


#@ ensures \result >= 0
#@ assigns \nothing
def f(x: Literal[1, 2]) -> int:
    if x == 1:
        return 0
    return 1


if __name__ == "__main__":
    assert f(1) == 0
    assert f(2) == 1
    print("PASS")
