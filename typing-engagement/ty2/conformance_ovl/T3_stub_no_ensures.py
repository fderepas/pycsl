"""Static gate T3 — stub with NO `#@ ensures` contributes no guarded postcondition.

Spec clause O3 (§1.1): "A stub with no postcondition contributes no guarded
clause (its guard is still synthesized for selection but it adds no VC)."

This driver: ONE `@overload` stub `f(x: int) -> int` with NO `#@ ensures`. The
implementation `def f(x: int) -> int: return x`. No guarded postcondition is
synthesized (the stub contributes no VC). The call site `f(5)` has no extra
postcondition beyond the implementation's own.

Expected (from spec): prove — no guarded-postcondition VC is emitted for the
stub; the call site typechecks and the implementation's own (empty) postcondition
discharges.
"""

from typing import overload


@overload
def f(x: int) -> int: ...


def f(x: int) -> int:
    return x


#@ requires True
#@ ensures True
#@ assigns \nothing
def g() -> int:
    return f(5)


if __name__ == "__main__":
    assert g() == 5
    print("PASS")
