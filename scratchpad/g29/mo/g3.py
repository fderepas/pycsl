r"""math.comb"""
import math
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    return math.comb(3, 5) + 1


if __name__ == "__main__":
    print("CPython:", probe())
