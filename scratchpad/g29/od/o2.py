r"""old of scalar param rebinding"""
from typing import List
_ = 0  # anchor


#@ ensures \result == \old(x) + 1
def f(x: int) -> int:
    x = x + 10
    return x + 1


#@ ensures \result == 3
def probe() -> int:
    return f(2)


if __name__ == "__main__":
    print("CPython:", probe())
