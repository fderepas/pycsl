from typing import NoReturn

FLAG = True

if FLAG:
    #@ requires x > 0 and x < 0
    #@ ensures \result == 99
    def f(x: int) -> int:
        return 1
else:
    def f(x: int) -> NoReturn:
        raise ValueError("x")
