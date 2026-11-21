from typing import Dict

#@ no_exception \all
def f(d: Dict[int, int], e: Dict[int, int]) -> int:
    for k in (x for x in e):
        d[k + 300] = 0
    return 0
