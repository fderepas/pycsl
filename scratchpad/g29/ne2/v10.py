r"""bytes index out of range"""
import math
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    b = bytes([1])
    v = b[3]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
