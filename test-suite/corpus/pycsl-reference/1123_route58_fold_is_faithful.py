"""Test 1123 — ROUTE #58 POSITIVE control, and the interesting one: the repair did not
merely fail closed, it RECOVERED a true claim the exact-real model could not prove.

TRUE OF THE PROGRAM: `(1/3) == 0.3333333333333333` is `True` in Python — the literal
is the shortest decimal that round-trips to the same double.

**THIS FILE FAILED AT HEAD AND PASSES AFTER THE REPAIR.** Under the exact-real
lowering one third was NOT the terminating decimal, so a claim that is true of the
program was unprovable. The old model was therefore UNSOUND on orderings (1121, 1122)
and, right next door, INCOMPLETE on equalities whose quotient is not representable.
Both directions were wrong, in opposite ways.

WHY FOLDING IS SOUND, which is the whole design. Two int literals are folded exactly
as CPython folds them and rendered through the SAME normalization the float-literal
leaf uses (`repr` of the binary64 value). That rendering is injective on doubles and
order-preserving — two distinct doubles differ by at least one ulp, so their half-ulp
rounding intervals are disjoint — and a float LITERAL in the source goes through the
identical normalization (`0.10000000000000001` emits as `0.1`). So a folded quotient
and a literal compare in the model exactly as the two doubles compare in Python. The
fold does not re-introduce the bug at a finer scale; it is what makes the model agree
with the language.
"""
_ = 0  # anchor


#@ ensures \result == 0.3333333333333333
#@ assigns \nothing
def f() -> float:
    return 1 / 3
