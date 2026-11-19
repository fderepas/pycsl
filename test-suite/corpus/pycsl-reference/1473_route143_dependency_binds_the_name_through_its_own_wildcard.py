r"""Test 1473 - ROUTE #143 carrier-rerun on gen #29's own draft 2: the callee's module obtains `LIM` only through ITS OWN `from consts import *`, so a dependency-bound-name set built from its explicit bindings missed it and `no_exception ValueError` PROVED (val `(5) < 0`); CPython raises. Wildcard sources are now followed transitively on both sides.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r143_starlib import f3

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f3(k)

