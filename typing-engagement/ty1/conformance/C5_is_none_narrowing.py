"""Static gate C5 — `is None` narrowing.

Spec clause C5 (union-twoplane-spec.md §1.2): after `if x is None:` on a
value of type `Union[A, None]`, the False branch narrows `x` to type `A`.
The True branch returns a constant; the False branch uses `x` as an int
(narrowing must discharge the int-operator obligation on `x`).

Expected (from spec): prove (narrowing VC on the False branch).
"""

from typing import Union


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def f(x: Union[int, None]) -> int:
    if x is None:
        return 0
    return x


if __name__ == "__main__":
    assert f(1) == 1
    assert f(None) == 0
    print("PASS")
