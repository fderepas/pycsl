from typing import Tuple

#@ requires True
#@ ensures \result[1] == "a"
def f(x: float, b: int) -> Tuple[float, str]:
    if b > 0:
        return x, "a"
    return 0.5, "a"
