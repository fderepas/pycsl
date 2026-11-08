r"""assigns a range but writes outside it"""
from typing import List
_ = 0  # anchor


#@ requires \length(a) == 4
#@ assigns a[0..1]
def f(a: List[int]) -> None:
    a[3] = 9


#@ ensures \result == 0
def probe() -> int:
    a: List[int] = [0, 0, 0, 0]
    f(a)
    return a[3]


if __name__ == "__main__":
    print("CPython:", probe())
