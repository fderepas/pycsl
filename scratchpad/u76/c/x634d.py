from typing import List
from m634d import f


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def g(xs: List[int]) -> int:
    f(xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython g([0]) =", g([0]))
