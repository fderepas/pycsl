r"""Test 1400 — ROUTE #136: #118's rule keys on a SUBSCRIPT STORE through the namespace dict, so handing that dict to another writer walks past it — `operator.setitem(globals(), "N", 5)` PROVED `f() == 3` while CPython returns 5. A no-argument `globals()`/`vars()`/`locals()` IS the module namespace and may now only be bound to a plain name or read through a subscript (`vars(self)` has an argument and is untouched).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import operator

N = 3
operator.setitem(globals(), "N", 5)


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
