r"""Test 2207 — route #239 (expected FAIL): route #41 made a READ of an erased local (tuple/set
literal, generator) the per-NAME constant `pycsl_erased_x` and left the binding `x := 0`, so
every value `x` ever held was one term: `(1, 2) == (3, 4)` PROVED at f926a808 (CPython
False, `f()` = 0). The binding now stores a fresh `(any int)` and the read is `!x`.
Control (one binding read twice): 2213.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = (1, 2)
    a = x
    x = (3, 4)
    b = x
    if a == b:
        return 1
    return 0
