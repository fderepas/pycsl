r"""range negative step length"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    n = 0
    for i in range(5, 0, -2):
        n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
