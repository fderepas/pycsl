"""Static gate L1 (negative) — value outside the set must be REJECTED.

Spec clause L1 (literal-twoplane-spec.md §1.1, S5 case (b)): a value equal
to NO `v_i` flowing into a `Literal[v1, ..., vn]` target must be REJECTED.
The synthesized `requires { x = 1 \/ x = 2 }` precondition must NOT be
discharged when the caller passes `x = 3` (no disjunct holds).

Concretely: this driver calls `f` with a literal `3` that is provably
outside the value set {1, 2}. The precondition VC fails — the call site
cannot prove `3 == 1 \/ 3 == 2`.

Expected (from spec): FAIL (precondition VC at the call site fails).
"""

from typing import Literal


#@ ensures \result == x
#@ assigns \nothing
def f(x: Literal[1, 2]) -> int:
    return x


#@ ensures \result == 3
def caller() -> int:
    return f(3)


if __name__ == "__main__":
    # The runtime would print PASS (no enforcement); the static gate FAILs.
    print("PASS")
