r"""G29 CG-S6 — route #154 carrier: the field's container is passed to a MUTATING function."""
from typing import List
_ = 0  # anchor


#@ requires len(ys) >= 1
#@ assigns ys[0]
def poke(ys: List[int]) -> None:
    ys[0] = 9


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]
        poke(self.xs)


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
