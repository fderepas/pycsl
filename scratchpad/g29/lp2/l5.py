r"""range evaluated once"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 10
def probe() -> int:
    n = 3
    c = 0
    for i in range(n):
        n = 10
        c = c + 1
    return c


if __name__ == "__main__":
    print("CPython:", probe())
