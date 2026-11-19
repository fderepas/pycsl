r"""Test 2479 — route #252 (expected FAIL): under `#@ no_exception \all`, `y = x - x` on `x: Any` was a
total uninterpreted `pycsl_py_sub` and PROVED exception-free. CPython: a user `__sub__` raises
ValueError. PROVED at 15f8c4bd; the erased operation now carries an unprovable obligation.
"""
# pycsl-expected: FAIL
from typing import Any


#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    y = x - x
    return 1


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            raise ValueError("no")

    try:
        f(P())
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
