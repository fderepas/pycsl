"""Test 0622 — negative: a range quantifier genuinely constrains (07-1311 Q1.2, non-vacuity).

`\\forall i in range(2); i >= 1` is FALSE (i = 0 violates it), so the quantifier must be refuted —
proving the `in range(...)` domain is the real `0 <= i < 2` bound, not a vacuous/dropped domain.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


#@ ensures \forall i in range(2); i >= 1
#@ assigns \nothing
def g() -> int:
    return 0
