r"""G29 CG-S1 — `__init__` writes an ELEMENT of a list field it just initialised."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]
        self.xs[0] = 9


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
