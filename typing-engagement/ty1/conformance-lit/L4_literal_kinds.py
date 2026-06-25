"""Static gate L4 — supported literal kinds (int/str/bool/None all work).

Spec clause L4 (literal-twoplane-spec.md §1.4): the supported literal kinds
are int, str, bool (which are int literals by S1 — bool → 1/0), and None
(→ 0). Each kind must synthesize a ground `requires` clause that Why3
discharges as a standard precondition VC.

This driver exercises each supported kind as a separate function and expects
every one to typecheck + prove.

Expected (from spec): PASS for all four kinds (int, str, bool, None).
"""

from typing import Literal


#@ ensures \result == x
#@ assigns \nothing
def int_kind(x: Literal[1, 2]) -> int:
    return x


#@ ensures \result == x
#@ assigns \nothing
def str_kind(x: Literal["a", "b"]) -> str:
    return x


#@ ensures \result == x
#@ assigns \nothing
def bool_kind(x: Literal[True, False]) -> int:
    return x


#@ ensures \result == x
#@ assigns \nothing
def none_kind(x: Literal[None]) -> int:
    return x


if __name__ == "__main__":
    assert int_kind(1) == 1
    assert str_kind("a") == "a"
    assert bool_kind(True) == 1
    assert none_kind(0) == 0
    print("PASS")
