r"""act requires only in guard"""
from typing import List
_ = 0  # anchor


#@ act pos:
#@     given x > 0
#@     requires x < 10
#@     ensures \result == 1
def f(x: int) -> int:
    return 10 // (10 - x)


#@ ensures \result == 1
def probe() -> int:
    return f(10)


if __name__ == "__main__":
    print("CPython:", probe())
