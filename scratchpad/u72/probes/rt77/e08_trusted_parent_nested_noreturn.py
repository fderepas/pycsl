from typing import NoReturn


#@ \trusted
#@ ensures \result == 1
def outer(y: int) -> int:
    def f(x: int) -> NoReturn:
        raise ValueError("x")
    return 1


#@ requires x > 0 and x < 0
#@ ensures \result == 99
def f(x: int) -> int:
    return 1
