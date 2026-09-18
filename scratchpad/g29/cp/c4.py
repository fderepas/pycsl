r"""list() constructor copy"""
import copy
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    a: List[int] = [0]
    b = list(a)
    b[0] = 5
    return a[0]


if __name__ == "__main__":
    print("CPython:", probe())
