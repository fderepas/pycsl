r"""mutual recursion even odd wrong"""
from typing import List
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == True
def even(n: int) -> bool:
    if n == 0:
        return True
    return odd(n - 1)


#@ requires n >= 0
#@ ensures \result == True
def odd(n: int) -> bool:
    if n == 0:
        return False
    return even(n - 1)


#@ ensures \result == True
def probe() -> bool:
    return even(1)


if __name__ == "__main__":
    print("CPython:", probe())
