r"""try in while with break on placeholder index"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = []
    n = 0
    i = 0
    #@ loop invariant 0 <= i and i <= 3
    #@ loop variant 3 - i
    while i < 3:
        try:
            v = xs[i]
        except IndexError:
            break
        n = n + 1
        i = i + 1
    return n + 3


if __name__ == "__main__":
    print("CPython:", probe())
