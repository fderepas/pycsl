r"""math.fmod zero"""
import math
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    f = math.fmod(1.0, 0.0)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
