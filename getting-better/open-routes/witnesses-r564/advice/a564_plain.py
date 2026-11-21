# advice probe (route #564): witness eu1200 following the advice -- compute the element in a plain statement first
from typing import List


#@ no_exception \all
def f(k: int, xs: List[int], t: str) -> int:
    c = k < len(t)
    w = (1, c)
    return 1
