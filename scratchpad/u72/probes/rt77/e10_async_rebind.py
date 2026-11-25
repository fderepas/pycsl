from typing import NoReturn


def f(x: int) -> NoReturn:
    raise ValueError("x")


#@ requires x > 0 and x < 0
#@ ensures \result == 99
async def f(x: int) -> int:
    return 1
