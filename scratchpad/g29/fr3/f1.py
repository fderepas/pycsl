r"""for expansion off-by-one upper bound"""
from typing import List
_ = 0  # anchor


#@ requires \length(data) == 3
#@ for k in range(0, 3):
#@     requires data[k] == 0
#@ ensures \result == 0
def f(data: List[int]) -> int:
    return data[0] + data[1] + data[2]


#@ ensures \result == 0
def probe() -> int:
    d: List[int] = [0, 0, 1]
    return f(d)


if __name__ == "__main__":
    print("CPython:", probe())
