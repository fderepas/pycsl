"""Static gate C2 — arm membership.

Spec clause C2 (union-twoplane-spec.md §1.1): a value of type `A_i` flowing
into a target of `Union[A_1, ..., A_n]` must be assignable to that Union —
i.e. an S5 case where `v: int` flows into `Union[int, str]` must typecheck
and prove. The function body returns a constant int.

Expected (from spec): typecheck + prove (per-arm VC discharge).
"""

from typing import Union


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def f(x: Union[int, str]) -> int:
    return 5


if __name__ == "__main__":
    assert f(1) == 5
    assert f("a") == 5
    print("PASS")
