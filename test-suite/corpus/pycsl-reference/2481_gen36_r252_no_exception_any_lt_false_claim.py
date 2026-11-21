r"""Test 2481 — route #252 (expected FAIL): under `#@ no_exception \all`, `x < y` on two `Any` values
PROVED exception-free. CPython: `1 < "a"` raises TypeError. PROVED at 15f8c4bd; the erased ordering
now carries an unprovable obligation.
"""
# pycsl-expected: FAIL
from typing import Any


#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if x < y:
        return 1
    return 1


if __name__ == "__main__":
    try:
        f(1, "a")
        raise AssertionError("expected TypeError")
    except TypeError:
        pass
