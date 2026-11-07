r"""Test 3815 -- gen #37 route #306 (expected PASS): CONTROL: `d.get(2, 10 // x)` with `x != 0` (missing key) proves `\result == 10 // x`.
"""
# pycsl-expected: PASS
from typing import Dict

#@ requires x != 0
#@ no_exception \all
#@ ensures \result == 10 // x
def f(x: int) -> int:
    d: Dict[int, int] = {1: 1}
    return d.get(2, 10 // x)

if __name__ == "__main__":
    assert f(3) == 3
