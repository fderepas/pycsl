r"""Test 1345 — ROUTE #124: `def inc` (+1) followed by `from lib import *` whose `inc` decrements; the star import rebinds `inc` at runtime (CPython 2) but the model PROVED `inc(3) == 4`. A star import after a module-scope binding is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


from multi_file_lib.r124_starlib import *


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
