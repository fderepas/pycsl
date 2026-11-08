# ROUTE #219 CONTROL 2 (expects REFUSED today — the UB detector working).
#
# The same loop in a plain function. `[!] PIPELINE ERROR: ... UB-7.1 — the loop body
# mutates the iterated collection 'xs'.`
from typing import List
_ = 0  # anchor


#@ ensures \result >= 0
def go(xs: List[int]) -> int:
    n: int = 0
    for x in xs:
        xs.append(x)
        n = n + 1
    return n
