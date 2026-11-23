from typing import NoReturn


class C:
    def __init__(self) -> None:
        self.v = 0

    def h(self, x: int) -> NoReturn:
        raise ValueError("x")

    #@ ensures \result == 1
    def m(self, y: int) -> int:
        #@ requires x > 0 and x < 0
        #@ ensures \result == 99
        def h(x: int) -> int:
            return 1
        return 1
