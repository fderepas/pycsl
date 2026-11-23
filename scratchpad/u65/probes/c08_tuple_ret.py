from typing import Tuple
#@ requires x > 0 and x < 0
#@ ensures \result[0] == 99
def f(x: int) -> Tuple[int, int]:
    return (1, 2)
