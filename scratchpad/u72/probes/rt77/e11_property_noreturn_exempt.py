from typing import NoReturn


class C:
    def __init__(self) -> None:
        self._v = 1

    @property
    def v(self) -> NoReturn:
        raise ValueError("x")

    #@ requires x > 0 and x < 0
    #@ ensures self._v == 99
    @v.setter
    def v(self, x: int) -> None:
        self._v = 2
