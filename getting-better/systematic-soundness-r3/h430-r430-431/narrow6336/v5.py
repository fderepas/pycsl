from typing import Dict

#@ no_exception \all
def f(d: Dict[int, int], k: int) -> int:
    d[k + 300] = 0
    return 0
