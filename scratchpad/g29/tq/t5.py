r"""augmented assign on tuple element of list"""
from typing import List, Tuple, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1]
    i = 0
    xs[i] += 1
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
