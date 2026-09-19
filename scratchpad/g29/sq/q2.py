r"""sorted does not mutate the source"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [3, 1, 2]
    ys = sorted(xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
