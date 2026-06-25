"""Static gate L1 — value-set membership (the load-bearing Literal clause).

Spec clause L1 (literal-twoplane-spec.md §1.1): a parameter annotated
`x: Literal[v1, ..., vn]` carries the static obligation `requires x == v1
or ... or x == vn` (ground requires). The synthesized requires is a
finite disjunction of concrete-value equalities; the postcondition
`\result == x` discharges under it (the input is one of {1, 2} and the
function returns it unchanged).

Expected (from spec): typecheck + prove (synthesized requires VC discharges).
"""

from typing import Literal


#@ ensures \result == x
#@ assigns \nothing
def f(x: Literal[1, 2]) -> int:
    return x


if __name__ == "__main__":
    assert f(1) == 1
    assert f(2) == 2
    print("PASS")
