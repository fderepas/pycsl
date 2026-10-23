r"""uncaught empty list index"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    return xs[0] * 0
