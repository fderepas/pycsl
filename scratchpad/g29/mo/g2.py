r"""math.isqrt"""
import math
from typing import List
_ = 0  # anchor


#@ ensures \result == 4
def probe() -> int:
    return math.isqrt(15)


if __name__ == "__main__":
    print("CPython:", probe())
