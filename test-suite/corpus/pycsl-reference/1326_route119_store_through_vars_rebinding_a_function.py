r"""Test 1326 — ROUTE #119: `vars()["inc"] = dec` at module level rebinds `inc`; #118 knew only `globals()`. `inc(3)` PROVED `\result == 4`, CPython 2. Refused.
"""
# pycsl-expected: FAIL
#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


#@ ensures \result == y - 1
#@ assigns \nothing
def dec(y: int) -> int:
    return y - 1


vars()["inc"] = dec


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
