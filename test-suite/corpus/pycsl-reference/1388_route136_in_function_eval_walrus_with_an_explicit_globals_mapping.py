r"""Test 1388 — ROUTE #136: the `eval` arm of test 1387. `eval("(N := 5)", globals())` inside a function rebinds the module global; `f()` PROVED `\result == 3` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    eval("(N := 5)", globals())
    return N
