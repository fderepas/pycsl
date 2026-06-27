"""Static gate P4/P5 — THE GT7 NO-BLEND WITNESS: presence does NOT satisfy static
conformance.

Spec clause P4 (§1.1): "The conformance obligation is a per-method VC, NOT a
presence check. ... A lowering that let attribute presence satisfy the static
conformance obligation would blend the planes."
Spec clause P5 (§1.2): "conformance is contract refinement, NOT attribute
presence. ... One S5 case: a class with attribute presence (passes runtime
isinstance) but a non-refining contract FAILS static conformance — the
load-bearing no-blend witness."
Spec clause D1 (§3): "a class C can PASS the runtime isinstance (all members
present) while FAILING static conformance (a member's contract does not refine
P.m's). A lowering that let the weak runtime presence check SATISFY the static
full-signature conformance obligation would blend the planes — this is the GT7
canonical failure."

This driver is the load-bearing no-blend witness for the STATIC side: `Square`
HAS the `draw` method (method PRESENCE — it would pass a runtime `@runtime_checkable`
isinstance check), but its contract `\result >= -100` is a WEAKER post than the
protocol's `\result >= 0` (the refinement `result >= -100 -> result >= 0` does
NOT hold). The static conformance refinement goal
`square__draw_refines_drawable` must FAIL — proving that the static conformance
is a per-method contract-refinement VC, INDEPENDENT of method presence.

If this driver PASSED, the GT7 no-blend check would be BROKEN — the static
conformance would have been discharged by method presence (the runtime plane)
rather than by contract refinement (the static plane).

Expected (from spec): the refinement goal `square__draw_refines_drawable` is
UNPROVABLE (Unknown/Timeout) — verification FAILS. This is the keystone: a class
with method presence but a non-refining contract FAILS static conformance.
"""

# pycsl-expected: FAIL

from typing import Protocol


class Drawable(Protocol):
    #@ ensures \result >= 0
    def draw(self) -> int: ...


#@ conforms_to Drawable
class Square:
    # WEAKER post: `result >= -100 -> result >= 0` does NOT hold.
    # Method PRESENCE holds (Square has `draw`), but the contract does NOT refine.
    #@ ensures \result >= -100
    def draw(self) -> int:
        return 10


if __name__ == "__main__":
    print("PASS")
