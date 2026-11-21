r"""Test 3811 -- gen #37 route #306 (expected FAIL): `Dict[str, PyVal]` form of 3801 (`HInt`-wrapped default).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ requires "k" in d
#@ no_exception \all
#@ assigns \nothing
def f(d: Dict[str, PyVal], x: int) -> int:
    y = d.get("k", 10 // x)
    return 0

if __name__ == "__main__":
    assert f({"k": 1}, 0) == 0
