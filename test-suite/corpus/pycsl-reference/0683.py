"""Test 0683 — negative: KEYWORD-ONLY mutable default argument.

`def f(x, *, acc=[])` — the keyword-only case the old positional-only `param_defaults`
would have MISSED. The migration computes `has_mutable_default` over ALL defaults
(positional + kw) in the front-end, closing that gap. Characterization test (Phase B).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
def f(x: int, *, acc=[]) -> int:
    return x
