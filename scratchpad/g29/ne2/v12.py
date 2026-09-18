r"""list slice assignment with extended step size mismatch"""
import math
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2, 3, 4]
    xs[::2] = [9]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
