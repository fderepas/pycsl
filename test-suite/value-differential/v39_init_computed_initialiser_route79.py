"""v39 DISAGREE — ROUTE #79. `self.n = len(items)` is an `__init__` initialiser whose RHS
names something OUTSIDE the parameter set, so the field used to fall back to a literal `0`
and this false claim PROVED. The repair makes the field UNCONSTRAINED, so it now refuses.
CPython returns 3."""
from typing import List


class C:
    n: int

    #@ assigns self.n
    def __init__(self, items: List[int]) -> None:
        self.n = len(items)


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C([1, 2, 3])
    return c.n


if __name__ == "__main__":
    print(f())
