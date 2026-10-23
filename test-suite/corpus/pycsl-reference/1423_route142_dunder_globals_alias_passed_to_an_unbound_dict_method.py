r"""Test 1423 — ROUTE #142, third shape, through the attribute spelling: `_g = f.__globals__; dict.update(_g, N=5)` PROVED `f() == 3`; CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


_g = f.__globals__
dict.update(_g, N=5)