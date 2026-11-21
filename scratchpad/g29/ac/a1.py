r"""act guard read in pre-state with param rebinding"""
from typing import List
_ = 0  # anchor


#@ act neg:
#@     given x < 0
#@     ensures \result == 100
#@ act pos:
#@     given x >= 0
#@     ensures \result == x
def f(x: int) -> int:
    x = x - 10
    return x + 10


#@ ensures \result == 100
def probe() -> int:
    return f(-1)


if __name__ == "__main__":
    print("CPython:", probe())
