r"""assert in while"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= 1
    #@ loop variant 1 - i
    while i < 1:
        assert i == 7
        i = i + 1
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
