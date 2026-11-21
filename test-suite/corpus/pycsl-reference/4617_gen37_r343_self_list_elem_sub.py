r"""Test 4617 -- gen #37 route #343 (expected FAIL): witness h08: `xs = [self]; xs[0] - xs[0]` with a user `__sub__` returning 1; `ensures \result == 0` PROVED (CPython 1). REFUSED (erased element into `-> int`).
"""
# pycsl-expected: FAIL
from typing import List
class W:
    def __sub__(self, o: object) -> int:
        return 1
    #@ ensures \result == 0
    def m(self) -> int:
        xs = [self]
        return xs[0] - xs[0]

if __name__ == "__main__":
    assert W().m() == 1
