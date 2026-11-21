r"""math.factorial small"""
import math
from typing import List
_ = 0  # anchor


#@ ensures \result == 6
def probe() -> int:
    return math.factorial(4)


if __name__ == "__main__":
    print("CPython:", probe())
