r"""Test 3808 -- gen #37 route #306 (expected FAIL): str-keyed form of 3801.
"""
# pycsl-expected: FAIL
from typing import Dict

#@ no_exception \all
#@ ensures \result == 1
def f(x: int) -> int:
    d: Dict[str, int] = {"a": 1}
    return d.get("a", 10 // x)

if __name__ == "__main__":
    assert f(0) == 1
