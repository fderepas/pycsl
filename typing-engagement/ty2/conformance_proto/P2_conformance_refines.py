"""Static gate P2 — conformance: per-method contract refinement.

Spec clause P2 (§1.1, the load-bearing rule): "A class C conforms to protocol P
iff, for every member m of P, C has a method m whose contract REFINES P.m's
contract: requires(C.m) ⟹ requires(P.m) (weaker-or-equal pre), ensures(P.m) ⟹
ensures(C.m) (stronger-or-equal post), assigns(C.m) ⊆ assigns(P.m)."

This driver is the load-bearing conformance witness: `Square` conforms to
`Drawable` because its `draw` carries the STRONGER post `\result >= 5` (a
stronger post refines: `result >= 5 -> result >= 0` holds).

Expected (from spec): prove — the per-method refinement goal
`((pre_P -> pre_C) /\ (post_C -> post_P))` discharges: `result >= 5 -> result
>= 0` is valid, so `square__draw_refines_drawable` is Valid.
"""

from typing import Protocol


class Drawable(Protocol):
    #@ ensures \result >= 0
    def draw(self) -> int: ...


#@ conforms_to Drawable
class Square:
    #@ ensures \result >= 5
    def draw(self) -> int:
        return 5


#@ ensures \result >= 5
def use() -> int:
    return 5


if __name__ == "__main__":
    assert use() == 5
    print("PASS")
