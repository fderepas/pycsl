r"""Test 1346 — ROUTE #124 (carrier of the first draft): two star imports both exporting `inc`; the LATER one wins at runtime (+1, CPython 4) but the wildcard resolver kept the first and PROVED `inc(3) == 2`. A second star import is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r124_starlib import *
from multi_file_lib.r119_plainlib import *


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return inc(3)
