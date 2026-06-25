"""Test 0732 — `Literal[1, 2]` narrowing by equality (L2).

typing-engagement ty1 (26-0000-typing-spec-2): after `if x == 1:` where
`x: Literal[1, 2]`, the True branch narrows to `Literal[1]` (path condition
`x = 1`) and the False branch narrows to `Literal[2]` (the residual disjunct,
since `x = 1` is ruled out and the precondition's `x = 1 \/ x = 2` leaves only
`x = 2`). The static narrowing is emergent from the standard path-condition VC
on the existing `if x == v` lowering — NO new IR node, NO new VC kind. Both
branches return a distinct int (0 on True, 1 on False); the postcondition
`\result >= 0` discharges on both paths.
"""
from typing import Literal

#@ ensures \result >= 0
#@ assigns \nothing
def branch(x: Literal[1, 2]) -> int:
    if x == 1:
        return 0
    return 1

if __name__ == "__main__":
    assert branch(1) == 0
    assert branch(2) == 1
    print("PASS")
