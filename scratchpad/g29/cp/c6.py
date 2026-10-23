r"""copy.deepcopy nested"""
import copy
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    a: List[List[int]] = [[0]]
    b = copy.deepcopy(a)
    b[0][0] = 5
    return a[0][0]


if __name__ == "__main__":
    print("CPython:", probe())
