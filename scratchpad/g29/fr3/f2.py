r"""for expansion over an index beyond the array"""
from typing import List
_ = 0  # anchor


#@ requires \length(data) == 2
#@ for k in range(0, 3):
#@     requires data[k] >= 0
#@ ensures \result == 0
def f(data: List[int]) -> int:
    return 0


#@ ensures \result == 0
def probe() -> int:
    d: List[int] = [0, 0]
    return f(d)


if __name__ == "__main__":
    print("CPython:", probe())
