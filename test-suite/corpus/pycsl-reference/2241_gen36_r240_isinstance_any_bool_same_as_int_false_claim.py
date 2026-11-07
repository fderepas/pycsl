r"""Test 2241 — route #240 (expected FAIL): on an `Any` subject the bool test was the SAME TERM as
the int test — both `(typeof_op x) = 0` — so inside `isinstance(x, int)` the bool test was
decided true and `\result == 1` PROVED at 1e4b380e while CPython `f(5)` = 0. The bool test is
now undecided, independent of the int test, and the postcondition is unproved.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    if isinstance(x, int):
        if isinstance(x, bool):
            return 1
        return 0
    return 1
