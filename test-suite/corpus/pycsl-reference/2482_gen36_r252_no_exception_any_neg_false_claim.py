r"""Test 2482 — route #252 (expected FAIL): under `#@ no_exception \all`, unary `-x` on `x: Any`
(route #251's `pycsl_py_neg`) PROVED exception-free. CPython: `-"a"` raises TypeError.
PROVED at 15f8c4bd; the erased operation now carries an unprovable obligation.
"""
# pycsl-expected: FAIL
from typing import Any


#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    y = -x
    return 1


if __name__ == "__main__":
    try:
        f("a")
        raise AssertionError("expected TypeError")
    except TypeError:
        pass
