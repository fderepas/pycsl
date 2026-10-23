r"""act on raise path"""
from typing import List
_ = 0  # anchor


#@ act neg:
#@     given x < 0
#@     ensures \result == 7
#@ complete neg
def f(x: int) -> int:
    if x < 0:
        raise ValueError()
    return 7


#@ ensures \result == 7
def probe() -> int:
    return f(-1)


if __name__ == "__main__":
    print("CPython:", probe())
