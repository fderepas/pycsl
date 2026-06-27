"""Static gate T1 — guard synthesis + call-site selection (int overload).

Spec clause O2 (overload-twoplane-spec.md §1.1): for each overload stub with
parameter `p_i: T_i`, the static plane synthesizes a guard `G_i` — a predicate
true iff the argument's static type is assignable to `T_i`. For TY2 (monomorphic)
`G_i = isinstance(p_i, T_i)`.

Spec clause O4 (§1.1): at a call site `f(v)` where `v` has static type `T_v`, the
active overload is the first stub whose guard `G_i` is satisfied by `T_v`. The
selected stub's guarded postcondition `G_i -> Q_i` applies. The selection is a
type-based VC.

This driver: ONE `@overload` stub `f(x: int) -> int` with `#@ ensures \result == x`,
implementation `def f(x: int) -> int: return x`, call site `f(5)` expecting `\result == 5`.

Expected (from spec): typecheck + prove — the int stub's guard selects, its
postcondition `\result == x` applies at the call site, and `f(5)` proves `\result == 5`.
"""

from typing import overload


#@ ensures \result == x
@overload
def f(x: int) -> int: ...


def f(x: int) -> int:
    return x


#@ ensures \result == 5
def g() -> int:
    return f(5)


if __name__ == "__main__":
    assert g() == 5
    print("PASS")
