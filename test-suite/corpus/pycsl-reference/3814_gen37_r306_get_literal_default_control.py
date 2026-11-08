r"""Test 3814 -- gen #37 route #306 (expected PASS): CONTROL: literal defaults stay byte-identical and prove.
"""
# pycsl-expected: PASS
from typing import Dict

#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    d: Dict[int, int] = {1: 1}
    return d.get(1, 5) + d.get(2, 0) - d.get(3, 0)

if __name__ == "__main__":
    assert f() == 1
