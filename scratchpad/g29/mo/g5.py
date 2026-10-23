r"""math.copysign"""
import math
from typing import List
_ = 0  # anchor


#@ ensures \result == 1.0
def probe() -> float:
    return math.copysign(1.0, -0.0)


if __name__ == "__main__":
    print("CPython:", probe())
