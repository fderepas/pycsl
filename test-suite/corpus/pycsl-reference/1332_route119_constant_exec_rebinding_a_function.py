r"""Test 1332 — ROUTE #119: a constant `exec("inc = dec")` at module level rebinds `inc` inside a string the rebinding refusal never looked into; `inc(3)` PROVED `\result == 4`, CPython 2. A constant exec naming a def/class/imported object is refused.
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


exec("inc = dec")


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
