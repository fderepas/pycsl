r"""Test 2480 — route #252 (expected FAIL): under `#@ no_exception \all`, `x == x` on `x: Any` (route
#249's uninterpreted `pycsl_py_eq`) PROVED exception-free. CPython: a user `__eq__` raises ValueError.
PROVED at 15f8c4bd; the erased comparison now carries an unprovable obligation.
"""
# pycsl-expected: FAIL
from typing import Any


#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    if x == x:
        return 1
    return 1


if __name__ == "__main__":
    class P:
        def __eq__(self, o: object) -> bool:
            raise ValueError("no")

    try:
        f(P())
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
