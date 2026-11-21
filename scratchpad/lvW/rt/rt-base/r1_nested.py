from typing import Tuple

#@ requires True
#@ ensures True
def f(x: int) -> Tuple[Tuple[int, int], str]:
    if x > 0:
        return (1, 2), "pos"
    return (3, 4), "neg"
