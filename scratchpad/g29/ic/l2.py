r"""loop variant not decreasing"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    i = 0
    #@ loop invariant i >= 0
    #@ loop variant 10
    while i < 3:
        i = i + 1
    return i


if __name__ == "__main__":
    print("CPython:", probe())
