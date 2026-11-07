r"""uncaught empty list index, nonzero use"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    xs: List[int] = []
    return xs[0] + 5
