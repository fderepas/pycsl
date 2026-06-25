"""NO-BLEND check (sharpened for Literal) — narrowing WITHOUT an equality guard.

Spec clause LD2 (literal-twoplane-spec.md §3, sharpening L2): the static
L2 narrowing (by equality `if x == v1:`) must NOT be discharged by the
runtime `x == v1` comparison. The static narrowing is a proof-time
path-condition judgment; the runtime test is a value-level comparison the
program performs. A lowering that let the runtime `x == v1` test's
outcome SATISFY the L2 narrowing obligation would blend the planes.

This is the NO-BLEND probe for LD2: a driver that claims a narrowing
WITHOUT the `if x == v1` guard but STILL uses `x` as if it were narrowed
to a specific value. If the lowering blends the planes — i.e. the runtime
`x == v1` semantics leak into the static judgment and the driver would
PASS because the runtime test "would narrow at runtime if executed" —
this driver would INCORRECTLY PASS. If the lowering is faithful, the
static plane refuses to narrow without an equality guard and the driver
FAILS (the postcondition `\result == 1` cannot be discharged because
`x` is only known to be in {1, 2}, not provably equal to 1).

Concretely: this driver returns `x` directly while claiming
`\result == 1`. With `x: Literal[1, 2]`, the static plane knows only
`x = 1 \/ x = 2`; without an `if x == 1:` guard, `x` is NOT narrowed to
`Literal[1]`, so `\result == 1` is unprovable (it would also hold for
`x = 2`).

Expected (from spec): FAIL — no narrowing without an equality guard (L2
requires the guard; LD2 forbids the runtime test from substituting for
the static narrowing). If this driver PASSES, the runtime `x == v1` test
is blending the planes (LD2 violation).
"""

from typing import Literal


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Literal[1, 2]) -> int:
    return x


if __name__ == "__main__":
    # Runtime would print PASS for f(1) (no enforcement); the static gate
    # must FAIL because \result == 1 is unprovable without narrowing.
    assert f(1) == 1
    print("PASS")
