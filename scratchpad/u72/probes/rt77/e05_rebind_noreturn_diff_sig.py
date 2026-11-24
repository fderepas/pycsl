from typing import NoReturn


def f(x: int) -> NoReturn:
    raise ValueError("x")


#@ requires x > 0 and y < 0 and x < y
#@ ensures \result == 99
def f(x: int, y: int) -> int:
    return 1
