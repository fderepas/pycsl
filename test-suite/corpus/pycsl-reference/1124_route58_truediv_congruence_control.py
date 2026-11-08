"""Test 1124 — ROUTE #58 POSITIVE control: a non-literal division is UNINTERPRETED, but
it must still be DETERMINISTIC.

TRUE OF THE PROGRAM: `f(a, b)` returns `a / b`, so `\result == a / b` holds always.

The operands here are parameters, so nothing can be folded — representability is a
property of the VALUE and the bridge is declared over all `a b: int` before any value
is known. The lowering is therefore one uninterpreted symbol, and the cheap way to
write it is a `val` with no `ensures`, under which two evaluations of `a / b` may
answer differently and even this reflexive postcondition stops proving. `val function`
keeps it deterministic, so the body's term and the contract's term are the same term
and the goal closes by congruence while no exact-real value or ordering is decided.

Same design, and same control, as 1120 for float-operand arithmetic.
"""
_ = 0  # anchor


#@ ensures \result == a / b
#@ assigns \nothing
def f(a: int, b: int) -> float:
    return a / b
