from typing import NamedTuple

class T(NamedTuple):
    x: float

#@ ensures \result == 1
def f() -> int:
    a = T(float("nan"))
    b = T(float("nan"))
    if a == b:
        return 1
    return 0
