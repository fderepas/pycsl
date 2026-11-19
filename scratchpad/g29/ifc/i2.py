r"""interface requires weaker than definition"""
from typing import List
_ = 0  # anchor


#@ requires x >= 5
#@ interface requires x >= 0
#@ ensures \result == x
def f(x: int) -> int:
    return 10 // (x - 4) * 0 + x


#@ ensures \result == 0
def probe() -> int:
    return f(0)


if __name__ == "__main__":
    print("CPython:", probe())
