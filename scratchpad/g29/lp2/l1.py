r"""for loop mutating list being iterated (append)"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    xs: List[int] = [1, 2]
    n = 0
    for x in xs:
        if n < 3:
            xs[0] = x
        n = n + 1
    return n + xs[0] * 0


if __name__ == "__main__":
    print("CPython:", probe())
