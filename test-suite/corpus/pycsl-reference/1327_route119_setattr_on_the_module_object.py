r"""Test 1327 — ROUTE #119: `setattr(sys.modules[__name__], "inc", dec)` rebinds `inc` through a call. PROVED `\result == 4`, CPython 2. Refused.
"""
# pycsl-expected: FAIL
import sys

#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


#@ ensures \result == y - 1
#@ assigns \nothing
def dec(y: int) -> int:
    return y - 1


setattr(sys.modules[__name__], "inc", dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
