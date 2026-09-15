r"""Test 1399 — ROUTE #136: the same hole one level of indirection deeper — `eval("exec('N = 5')")`. PROVED `f() == 3`; CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3
eval("exec('N = 5')")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
