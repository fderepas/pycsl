from typing import List, Tuple

#@ requires True
#@ ensures True
def f(x: int) -> Tuple[List[int], str]:
    if x > 0:
        return [1], "pos"
    return [2], "neg"
