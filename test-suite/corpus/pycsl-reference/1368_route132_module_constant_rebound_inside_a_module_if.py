r"""Test 1368 — ROUTE #132 (compound arm): `N = 3` then `if FLAG == 0: N = 5`; the folder reads only the module's top-level statements, folded `N` to 3 and PROVED `f() == 3` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
FLAG = 0
N = 3
if FLAG == 0:
    N = 5


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
