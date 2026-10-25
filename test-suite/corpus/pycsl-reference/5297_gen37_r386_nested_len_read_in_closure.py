r"""Test 5297 -- gen #37 route #386 (expected FAIL): `def len` nested in a method, read from a further nested def; FAIL at base (timeout), REFUSED after (route #386).
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

        def inner() -> int:
            return len([1, 2, 3])
        return inner()


if __name__ == "__main__":
    r = W().m()
    print("VIOLATION m() =", r) if r != 3 else print("no violation")
