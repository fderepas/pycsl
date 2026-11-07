r"""G29 FR4 — `random.shuffle(xs)` on a local list, then a content claim."""
import random
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2, 3, 4, 5, 6, 7, 8]
    random.seed(0)
    random.shuffle(xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
