r"""swap list elements via tuple assignment"""
from typing import List, Tuple, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2]
    xs[0], xs[1] = xs[1], xs[0]
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
