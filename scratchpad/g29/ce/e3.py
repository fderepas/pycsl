r"""comprehension over an unmodelled call"""
from typing import List, Dict, Any
_ = 0  # anchor


import os


#@ ensures \result == 0
def probe() -> int:
    xs = [len(p) for p in os.listdir(".")]
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
