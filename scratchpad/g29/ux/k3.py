r"""property getter raising caught"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v = -1

    @property
    def pos(self) -> int:
        if self.v < 0:
            raise ValueError()
        return self.v


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        x = c.pos
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
