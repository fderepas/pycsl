r"""interface ensures stronger than definition"""
from typing import List
_ = 0  # anchor


#@ ensures \result >= 0
#@ interface ensures \result == 5
def f(x: int) -> int:
    return 1


#@ ensures \result == 5
def probe() -> int:
    return f(0)


if __name__ == "__main__":
    print("CPython:", probe())
