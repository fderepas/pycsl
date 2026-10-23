r"""Test 1386 — ROUTE #136: `exec_splice.py`'s docstring and `functions._has_dynamic_exec` both assert that `eval` "returns a value and does not inject names". False since Python 3.8: `eval("(N := 5)")` at module scope rebinds the folded `N`, and `f()` PROVED `\result == 3` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3
eval("(N := 5)")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
