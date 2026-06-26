"""Static gate F3 — Final does NOT narrow or refine the type.

Spec clause F3 (final-twoplane-spec.md §1.3): `x: Final[int]` has the
static type `int`, NOT a refined or singleton type (e.g. NOT `Literal[5]`).
`Final` adds the write-restriction (F1/F2); it does NOT add a value-set
refinement, a narrowing fact, or an assignability refinement. A
`Final[T]`-typed expression is assignable to `T` and vice versa without
any narrowing obligation.

This driver uses the Final name in arithmetic (`x + 1`), which requires
`x` to be of type `int` (not a narrowed singleton). If the lowering
blended Final with Literal-style narrowing (treating `x: Final[int] = 5`
as `x: Literal[5]`), the `x + 1` postcondition `\\result == 6` would
still hold, but the lowering would be conflating two distinct constructs.
The static gate here confirms the type is `int` (arithmetic compiles) and
the postcondition discharges — no narrowing obligation is emitted.

Expected (from spec): PASS — the type is `int`, arithmetic is well-typed,
and `\\result == 6` discharges.
"""

from typing import Final

x: Final[int] = 5


#@ ensures \result == 6
#@ assigns \nothing
def f() -> int:
    return x + 1


if __name__ == "__main__":
    assert f() == 6
    print("PASS")
