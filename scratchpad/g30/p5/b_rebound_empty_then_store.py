from typing import List


#@ no_exception IndexError
#@ ensures \result == 5
def probe(flag: int) -> int:
    xs: List[int] = []
    if flag > 0:
        xs = []
    xs[0] = 5
    return xs[0]
