"""Test 1120 — ROUTE #53 POSITIVE control: the repair must not buy soundness by
making float arithmetic USELESS.

TRUE OF THE PROGRAM: `double(x)` returns `x + x`, so `\result == x + x` holds for
every float, including the ones no exact real describes.

THIS IS THE CLAUSE THE DESIGN IS BUILT AROUND. The cheap way to close route #53 is a
non-deterministic `val` with no `ensures`, under which two evaluations of `x + x` may
answer differently and even this reflexive postcondition stops proving — a model that
says nothing about float arithmetic at all. The landed repair instead uses a
DETERMINISTIC uninterpreted symbol (`val function float_add_op`), so the body's term
and the contract's term are literally the same term and the goal closes by congruence
while no exact-real VALUE, sign or ordering is decided.

The honest cost sits next door in 0517, stated there rather than hidden: the
non-negativity clause `\result >= 0.0` no longer proves. That is a COMPLETENESS loss
in one direction, and it is not repairable by an IEEE-true-looking sign clause —
`a >= 0 -> b >= 0 -> result >= 0` reads as sound but its antecedent ranges over the
REAL, which does not distinguish NaN, and the identical shape was already measured to
refute for `*`, where Python's `0.0 * inf` is `nan` rather than `0.0`.
"""
_ = 0  # anchor


#@ ensures \result == x + x
#@ assigns \nothing
def double(x: float) -> float:
    return x + x
