r"""walrus in while condition"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2]
    n = 0
    i = 0
    #@ loop invariant 0 <= i and i <= 2
    #@ loop variant 2 - i
    while (k := i) < 2:
        n = n + k
        i = i + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
