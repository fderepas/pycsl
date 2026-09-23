r"""Test 1859 — ROUTE #213 CLOSED: two reads of the same `getattr` across a mutation.

Route #197 made the `getattr` device a PER-SITE constant so that two reads of the SAME
expression agree, and wrote the reason down: `(any int)` is fresh at every evaluation,
"and losing that equality is a real loss of faithfulness for no gain". That equality is a
CLAIM, and it is sound exactly while the thing being read CANNOT CHANGE BETWEEN THE READS.
A constant depends on nothing, so it survived a write:

    x = getattr(o, "a"); mutate(o); y = getattr(o, "a"); return x - y
    #@ ensures \result == 0        PROVED.  CPython answers -98 for an object with a = 1.

and the emission said why — `x := pycsl_getattr_missing_…; (mutate o);
y := pycsl_getattr_missing_…`, the device depending on nothing at all.

THE REPAIR IS THE ONE ROUTE #213's RECORD PRICED AS "THE FAITHFUL FIX": the per-site device
is now APPLIED TO `!_pyobj_state`. That keeps #197's equality exactly where #197 justified
it — two reads with no intervening write read the same state, so the same term (control
`1727`) — and loses it exactly across a write, because `setattr` is emitted
`writes { _pyobj_state }` so the two applications take different arguments.

Gen #30 took a REFUSAL instead and reverted it: keyed on the shape, it broke 44 of the 53
mirrors, because `getattr(self, "_x", {})` is how this compiler reads optional attributes.
The state-keyed device is keyed on the PROPERTY, and the mirror emission moves in exactly
ONE file (`module6_whyml/functions.mlw`, two devices, eight lines).

WHERE THE DEVICE STAYS A CONSTANT, and why that is not a compromise: inside a Why3
`let function` or a contract term, a mutable ref cannot be dereferenced at all
(`This function depends on external variables, it cannot be used as pure` — measured on
the mirror's `_is_constant_exec`). It is also exactly where the constant is SOUND: a pure
function has no effects, so no write can occur between two reads inside it. The rule is
the property, not the shape.

Companion: `1860` (the three-argument spelling, which had the identical defect) and the
control `1727`. Route #214 — one constant for two DIFFERENT receivers — is a separate
claim about the DEFAULT-keyed device and remains OPEN, blocked on local-type inference.
"""
# pycsl-expected: FAIL
from typing import Any

_ = 0  # anchor


#@ assigns o.a
def mutate(o: Any) -> None:
    o.a = 99


#@ assigns o.a
#@ ensures \result == 0
def f(o: Any) -> int:
    x = getattr(o, "a")
    mutate(o)
    y = getattr(o, "a")
    return x - y
