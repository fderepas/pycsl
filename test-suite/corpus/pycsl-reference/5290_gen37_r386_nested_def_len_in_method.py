r"""Test 5290 -- gen #37 route #386 (expected FAIL): `def len(xs): return 0` nested in a method, `len([1, 2, 3])` under `\result == 3` lowered to the builtin length; PROVED at base 5addbdeef (CPython 0). REFUSED (builtin rebound by a nested def, route #386).
"""
# pycsl-expected: FAIL
from typing import List


class W:
    def __init__(self) -> None:
        self.x: int = 0

    #@ ensures \result == 3
    #@ assigns \nothing
    def m(self) -> int:
        def len(xs: List[int]) -> int:
            return 0
        return len([1, 2, 3])


if __name__ == "__main__":
    r = W().m()
    print("VIOLATION m() =", r) if r != 3 else print("no violation")
