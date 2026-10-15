r"""Test 2208 — route #239 (expected FAIL): a `None`-AMBIGUOUS local (route #46: `None` on one
path, an int on another) was read as the per-NAME constant `pycsl_erased_x` — after `x = 6`
too — so `a == b` PROVED at f926a808 for `a = x` (5 on the `c > 0` path) and `b = x` (6);
CPython `f(1)` = 0. The bindings already store the real value or `pycsl_none`, so the read is
now the ordinary `!x`. Value-faithful control: 2215.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    x = None
    if c > 0:
        x = 5
    a = x
    x = 6
    b = x
    if a == b:
        return 1
    return 0
