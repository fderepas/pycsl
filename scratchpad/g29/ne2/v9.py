r"""tuple index out of range"""
import math
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    t: Tuple[int, int] = (1, 2)
    i = 5
    v = t[i]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
