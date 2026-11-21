from typing import Dict

#@ no_exception \all
def f(d: Dict[int, int]) -> int:
    for k in list(d.keys()):
        d[k] = 0
    return 0
