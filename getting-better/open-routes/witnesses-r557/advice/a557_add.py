# advice probe (route #557): witness df1202 following the advice -- the set operation `s.add(1)` instead of `s[0] = 1`
from typing import List, Set


#@ no_exception \all
def f(k: int, xs: List[int], s: Set[int]) -> int:
    s.add(1)
    return 1
