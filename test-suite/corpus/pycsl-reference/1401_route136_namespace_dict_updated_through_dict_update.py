r"""Test 1401 — ROUTE #136: the same hole spelled `dict.update(globals(), N=5)`. PROVED `f() == 3`; CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3
dict.update(globals(), N=5)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
