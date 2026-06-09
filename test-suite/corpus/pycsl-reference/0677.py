"""Test 0677 — negative: dynamic `\proj` index in a GHOST expression.

`_validate_proj_indices` rejects a non-literal `\proj` index; in a `#@ ghost` value the
context is `function 'f' (ghost 'g')`. Third surface twin of 0302. Characterization
test for the proj_indices IR migration (Phase B).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0 and n < 2
def f(n: int) -> int:
    #@ ghost p : tuple2 = \mktuple(10, 20)
    #@ ghost g = \proj(p, n)
    return 0
