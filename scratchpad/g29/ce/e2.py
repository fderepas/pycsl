r"""attribute read of an unmodelled module"""
from typing import List, Dict, Any
_ = 0  # anchor


import sys


#@ ensures \result == 0
def probe() -> int:
    v = sys.maxsize
    return v * 0 + (1 if v > 0 else 0)


if __name__ == "__main__":
    print("CPython:", probe())
