r"""assigns a single element writes another"""
from typing import List
_ = 0  # anchor


#@ requires \length(a) == 2
#@ assigns a[0]
def f(a: List[int]) -> None:
    a[1] = 9


#@ ensures \result == 0
def probe() -> int:
    a: List[int] = [0, 0]
    f(a)
    return a[1]


if __name__ == "__main__":
    print("CPython:", probe())
