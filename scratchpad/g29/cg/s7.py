r"""G29 CG-S7 — the field list is built from a PARAMETER list that the caller then mutates (aliasing)."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, ys: List[int]) -> None:
        self.xs = ys


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    ys = [1, 2]
    c = C(ys)
    ys[0] = 9
    return c.xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
