"""Static gate O3 — None is always assignable to Optional[X].

Spec clause O3 (optional-twoplane-spec.md §1.1): a value of type `None`
is assignable to `Optional[X]` for every `X`, unconditionally — the
`None` arm is always reachable. This is the defining asymmetry of
`Optional`. The driver returns `None` from an `Optional[int]`-typed
function, exercising the `Arm_None` injection path.

Expected (from spec): prove (the None-arm injection VC discharges).
"""

from typing import Optional


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(x: Optional[int]) -> Optional[int]:
    return None


if __name__ == "__main__":
    assert f(1) is None
    assert f(None) is None
    print("PASS")
