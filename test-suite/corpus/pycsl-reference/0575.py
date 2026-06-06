"""Test 0575 — negative: group-wide strict positivity in a mutual inductive.

The `with odd(...)` member's rule `odd_bad` puts `even` in the antecedent of a nested
implication — a NON-strictly-positive occurrence. Why3 checks positivity across the
whole `inductive … with …` group, so it rejects the declaration ("non strictly positive
occurrence"), guaranteeing the least fixpoint exists. Demonstrates that mutual-group
members are not a positivity loophole (cf. 0563 for the single-predicate case).

Committed `# pycsl-expected: FAIL` and STAYS failing.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ inductive even(n: int):
#@     even_zero: even(0)
#@     even_succ: \forall m: int; odd(m) ==> even(m + 1)
#@ with odd(n: int):
#@     odd_bad: \forall m: int; (even(m) ==> even(m)) ==> odd(m + 1)


#@ ensures even(2)
#@ assigns \nothing
def fact() -> int:
    return 0
