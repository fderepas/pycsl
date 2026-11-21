r"""Test 3801 -- gen #37 route #306 (expected FAIL): `d.get(1, 10 // x)` under `no_exception \all`: Python evaluates `10 // x` eagerly and raises ZeroDivisionError at x == 0 even though key 1 is present.
"""
# pycsl-expected: FAIL
from typing import Dict

#@ no_exception \all
#@ ensures \result == 1
def f(x: int) -> int:
    d: Dict[int, int] = {1: 1}
    return d.get(1, 10 // x)

if __name__ == "__main__":
    assert f(0) == 1
