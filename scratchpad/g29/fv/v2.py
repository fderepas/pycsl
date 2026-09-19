r"""callee raising through a field receiver"""
from typing import List, Dict
_ = 0  # anchor


class Inner:
    def __init__(self) -> None:
        self.k = 0

    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


class Outer:
    def __init__(self) -> None:
        self.inner = Inner()

    #@ ensures \result == 0
    def run(self) -> int:
        try:
            v = self.inner.go(-1)
        except ValueError:
            return 9
        return v * 0


if __name__ == "__main__":
    print("CPython:", Outer().run())
