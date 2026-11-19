from typing import Any, Tuple

#@ requires True
#@ ensures \result[1] == "a"
def f(x: Any, b: int) -> Tuple[Any, str]:
    return x, "a"
