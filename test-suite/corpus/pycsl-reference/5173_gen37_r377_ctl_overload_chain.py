r"""Test 5173 -- gen #37 route #377 (expected PASS): CONTROL: an `@overload` stub followed by its implementation in a class body is admitted: `c.get(3) == 1` (CPython ok).
"""
# pycsl-expected: PASS
from typing import overload

class C:
    def __init__(self) -> None:
        self.n = 1

    @overload
    def get(self, x: int) -> int: ...

    #@ ensures \result == 1
    #@ assigns \nothing
    def get(self, x: int) -> int:
        return 1

#@ ensures \result == 1
def f(c: C) -> int:
    return c.get(3)

if __name__ == "__main__":
    print(f(C()))
