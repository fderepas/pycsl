r"""math.trunc negative"""
import math
from typing import List
_ = 0  # anchor


#@ ensures \result == -3
def probe() -> int:
    return math.trunc(-2.5)


if __name__ == "__main__":
    print("CPython:", probe())
