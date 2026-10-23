"""v45 DISAGREE — ROUTE #87. A list field's literal kept its LENGTH and lost every ELEMENT to a
definite `0` (`Array.make 3 0`). Found by probing a SECOND operation on a carrier a control
table had already called fail-closed after testing `len()` alone. CPython returns 1."""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[0]


if __name__ == "__main__":
    print(f())
