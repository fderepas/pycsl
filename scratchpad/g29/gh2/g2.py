r"""at-label reads pre-state"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    x = 1
    #@ label L
    x = 2
    #@ assert \at(x, L) == 2
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
