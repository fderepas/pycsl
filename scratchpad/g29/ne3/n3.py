r"""no_exception IndexError in while loop index"""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2]
    i = 0
    s = 0
    #@ loop invariant 0 <= i and i <= 3
    #@ loop variant 3 - i
    while i < 3:
        s = s + xs[i]
        i = i + 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
