"""Test 0676 — negative: dynamic `\proj` index in a LOOP invariant.

Module 5's `_csl_proj` rejects a non-literal `\proj` index (B-final STEP 1); the guard
now reports the enclosing-function context `function 'f'` for every surface (it moved
out of Module 4's per-surface visit_While). Surface twin of 0302 (function).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0 and n < 2
def f(n: int) -> int:
    #@ ghost p : tuple2 = \mktuple(10, 20)
    i = 0
    #@ loop invariant \proj(p, n) >= 0
    while i < 1:
        i = i + 1
    return 0
