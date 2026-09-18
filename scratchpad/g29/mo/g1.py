r"""math.gcd negative"""
import math
from typing import List
_ = 0  # anchor


#@ ensures \result == -2
def probe() -> int:
    return math.gcd(-4, 6)


if __name__ == "__main__":
    print("CPython:", probe())
