r"""control: enumerate and zip tuple targets under no_exception ValueError"""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result >= 0
def probe() -> int:
    xs: List[int] = [1, 2]
    n = 0
    for i, v in enumerate(xs):
        n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
