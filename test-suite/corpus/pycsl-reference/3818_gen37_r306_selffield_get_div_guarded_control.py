r"""Test 3818 -- gen #37 route #306 (expected PASS): CONTROL: self-field `.get(1, 10 // x)` under `x != 0` and `no_exception \all` proves.
"""
# pycsl-expected: PASS
from typing import Dict

class C:
    def __init__(self) -> None:
        self.d: Dict[int, int] = {1: 1}

    #@ requires x != 0
    #@ no_exception \all
    def m(self, x: int) -> int:
        return self.d.get(1, 10 // x)

if __name__ == "__main__":
    assert C().m(2) == 1
