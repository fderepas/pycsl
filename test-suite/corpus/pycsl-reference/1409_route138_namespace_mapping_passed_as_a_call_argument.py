r"""Test 1409 — ROUTE #138: the mapping can reach a call as an ARGUMENT rather than a receiver. `operator.setitem(f.__globals__, "N", 5)` PROVED `f() == 3` while CPython returns 5. The four namespace-bearing attributes may now appear only in a name binding or a subscript read.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import operator

N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


operator.setitem(f.__globals__, "N", 5)