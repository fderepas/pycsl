from typing import Any, Dict, List


#@ ensures \result == 1
def g(xs: List[int]) -> int:
    y = xs.index(3)
    return 1
