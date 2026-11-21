r"""slice assignment changes length"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    xs[0:2] = [9]
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
