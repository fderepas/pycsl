r"""no_exception IndexError 2d list"""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    g: List[List[int]] = [[1], [2]]
    v = g[1][1]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
