from typing import NoReturn


class C:
    def __init__(self) -> None:
        self.v = 0

    def m(self, x: int) -> NoReturn:
        raise ValueError("x")


class c:
    def __init__(self) -> None:
        self.w = 0

    #@ requires x > 0 and x < 0
    #@ ensures \result == 99
    def m(self, x: int) -> int:
        return 1
