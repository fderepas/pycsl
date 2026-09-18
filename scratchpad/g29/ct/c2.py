r"""requires on length discharged by a stale model"""
from typing import List, Dict
_ = 0  # anchor


#@ requires \length(xs) == 2
#@ ensures \result == 0
def g(xs: List[int]) -> int:
    return 0


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1]
    xs.append(2)
    xs.append(3)
    return g(xs)


if __name__ == "__main__":
    print("CPython:", probe())
