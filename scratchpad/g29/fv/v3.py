r"""guarded method through a FIELD receiver"""
from typing import Dict
_ = 0  # anchor


class Inner:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


class Outer:
    def __init__(self) -> None:
        self.inner = Inner(0)

    #@ ensures \result == 5
    def run(self) -> int:
        self.inner.get()
        return 5


if __name__ == "__main__":
    print("CPython:", Outer().run())
