"""Test 0677 — negative: dynamic `\proj` index in a GHOST expression.

Module 5's `_csl_proj` rejects a non-literal `\proj` index (B-final STEP 1); the guard
now reports the enclosing-function context `function 'f'` for every surface (it moved
out of Module 4's per-surface ghost-value walk). Third surface twin of 0302.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0 and n < 2
def f(n: int) -> int:
    #@ ghost p : tuple2 = \mktuple(10, 20)
    #@ ghost g = \proj(p, n)
    return 0
