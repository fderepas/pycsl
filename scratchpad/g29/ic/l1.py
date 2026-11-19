r"""loop invariant true only on first iteration"""
from typing import List
_ = 0  # anchor


#@ ensures \result >= 0
def probe() -> int:
    i = 0
    s = 0
    #@ loop invariant s == 0
    #@ loop variant 3 - i
    while i < 3:
        s = s + 1
        i = i + 1
    return s - 5


if __name__ == "__main__":
    print("CPython:", probe())
