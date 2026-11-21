# advice probe (route #556): witness g1407/dh1202 iterating `range(k)` instead of `len`.
from typing import List


#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    c = 0
    for x in range(k):
        c += 1
    return c
