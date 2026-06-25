"""NO-BLEND check (sharpened for Optional) — narrowing without a guard.

Spec clause O7 (inherited from Union C8, optional-twoplane-spec.md
§1.2): in the absence of an `is None` / `isinstance` / `TypeIs` /
`TypeGuard` guard, the static type of an `Optional[X]`-typed variable
is NOT refined by any other predicate. An S5 case where a narrowing is
claimed WITHOUT a guard must be REJECTED.

This is the NO-BLEND probe for OD2 (optional-twoplane-spec.md §3): if
the static O6 narrowing obligation were being discharged by the RUNTIME
`is None` comparison (rather than by the static-plane Arm_None
constructor match), then a driver that omits the `is None` guard but
STILL claims the narrowed type would INCORRECTLY PASS — because the
runtime test would still be the only thing "proving" the narrowing,
and there is no runtime test here.

Concretely: this driver uses `x` as an `int` on a path where NO `is
None` guard has fired. If the lowering blends the planes, the runtime
`is None` semantics (which would narrow at runtime if executed) might
leak into the static judgment and the driver would PASS. If the
lowering is faithful, the static plane refuses to narrow without a
guard and the driver FAILS (the `return x` is a variant value, not an
`int`).

Expected (from spec): FAIL — no narrowing without a guard (O7). If
this driver PASSES, the runtime `is None` test is blending the planes
(OD2 violation).
"""

from typing import Optional


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(x: Optional[int]) -> int:
    return x


if __name__ == "__main__":
    assert f(1) == 1
    print("PASS")
