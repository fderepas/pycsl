"""Test 0669 — negative: `\length` on a dict is rejected (GHOST-expression surface).

Same `_validate_predicate_bases` check as 0667/0668, but in a `#@ ghost` assignment —
so the error context is `function 'f' (ghost 'g')`. Third distinct surface context
the B4 IR migration must reproduce verbatim.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def f(d: dict) -> int:
    #@ ghost g = \length(d)
    return 0
