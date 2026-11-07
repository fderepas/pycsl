r"""recursive function with wrong ensures but variant"""
from typing import List
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == 0
#@ decreases n
def f(n: int) -> int:
    if n == 0:
        return 0
    return f(n - 1) + 1


#@ ensures \result == 0
def probe() -> int:
    return f(3)


if __name__ == "__main__":
    print("CPython:", probe())
