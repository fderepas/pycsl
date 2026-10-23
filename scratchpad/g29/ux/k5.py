r"""method raising in a nested call argument caught"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v = 0

    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


def ident(x: int) -> int:
    return x


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        ident(c.go(-1))
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
