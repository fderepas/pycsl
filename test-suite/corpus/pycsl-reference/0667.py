"""Test 0667 — negative: `\length` on a dict is rejected (function-contract surface).

`_validate_predicate_bases` rejects `\length` applied to a dict/set (modelled as a
total map, no cardinality). This pins the check on the FUNCTION-CONTRACT surface —
the error context is `function 'f'`. Characterization test for the refactor.md B4
migration of this check onto the IR: the migrated check must reproduce this message
verbatim. Negative twin family with 0668 (loop) / 0669 (ghost).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \length(d) >= 0
def f(d: dict) -> int:
    return 0
