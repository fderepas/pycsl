r"""G29 GH2 — a ghost array store aliasing a PROGRAM array."""
from typing import List
_ = 0  # anchor


#@ ensures \result == 7
def probe() -> int:
    xs: List[int] = [1, 2]
    #@ ghost snap : array = \copy(xs)
    #@ ghost xs[0] = 7
    y = 0
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
