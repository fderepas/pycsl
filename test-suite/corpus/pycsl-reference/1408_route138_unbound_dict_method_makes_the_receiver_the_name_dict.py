r"""Test 1408 — ROUTE #138: the unbound-method spelling `dict.__setitem__(f.__globals__, "N", 5)` makes the sink receiver the name `dict`, which has no module-scope binding and so defaulted to FRESH. It PROVED `f() == 3` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
N = 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N


dict.__setitem__(f.__globals__, "N", 5)