r"""Test 1422 — ROUTE #142, second shape: `_g = globals(); operator.setitem(_g, "N", 5)` reaches the same mapping as an ARGUMENT. PROVED `f() == 3`; CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import operator

N = 3
_g = globals()
operator.setitem(_g, "N", 5)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N