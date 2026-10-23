r"""shallow copy of nested list shares inner"""
import copy
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    a: List[List[int]] = [[0]]
    b = a.copy()
    b[0][0] = 5
    return a[0][0]


if __name__ == "__main__":
    print("CPython:", probe())
