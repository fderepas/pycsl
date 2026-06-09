"""Test 0676 — negative: dynamic `\proj` index in a LOOP invariant.

`_validate_proj_indices` rejects a non-literal `\proj` index; inside a `#@ loop
invariant` the context is `while loop at line N inside function 'f'`. Surface twin of
0302 (function). Characterization test for the proj_indices IR migration (Phase B).
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
