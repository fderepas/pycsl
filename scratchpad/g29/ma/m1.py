r"""G29 MA1 — a METHOD mutates a list field through a LOCAL ALIAS while declaring `assigns \nothing`."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]

    #@ requires len(self.xs) >= 1
    #@ assigns \nothing
    def m(self) -> None:
        xs = self.xs
        xs[0] = 9


#@ requires len(c.xs) >= 1
#@ ensures \result == c.xs[0]
def probe(c: C) -> int:
    before = c.xs[0]
    c.m()
    return before


if __name__ == "__main__":
    c = C()
    print("CPython:", probe(c), c.xs[0])
