from typing import Any, Tuple

#@ requires True
#@ ensures \result[1] == "a"
def f(x: Any, b: int) -> Tuple[Any, str]:
    if b > 0:
        return x, "a"
    return x, "a"
