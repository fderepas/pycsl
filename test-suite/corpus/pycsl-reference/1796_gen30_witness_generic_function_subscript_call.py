r"""Test 1796 — WITNESS: `f[T](...)` subscripting a generic FUNCTION at a call site.

ROUTE #215. PEP 695 makes a generic CLASS subscriptable (`Box[int]()` RUNS), but a generic
FUNCTION is NOT: CPython 3.14 answers `TypeError: 'function' object is not subscriptable`.
PyCSL used to accept the call, fail to resolve it to the specialization, and ERASE it to
the per-name opaque `pycsl_erased_<var>` — so a local REBOUND from a second such call read
the SAME constant and the two values were proved EQUAL. Refused now.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == n
def ident[T](n: int) -> int:
    return n


#@ ensures \result == 0
def probe() -> int:
    a = ident[int](1)
    x = a
    a = ident[int](2)
    return x - a
