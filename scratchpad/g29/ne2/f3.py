r"""single-element unpack of empty list"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    x, = xs
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
