r"""Test 2323 — route #246 (expected FAIL): the `set` analogue. `requires x == y` forced the two
`isinstance(_, set)` tests (`(typeof_op _) = 4`) equal, so `\result == 1` PROVED at f777e2bd. CPython
`f({1}, frozenset({1}))` = 0 (`{1} == frozenset({1})`, only the first is a `set`).
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if isinstance(x, set):
        if not isinstance(y, set):
            return 0
    return 1


if __name__ == "__main__":
    assert f({1}, frozenset({1})) == 0
