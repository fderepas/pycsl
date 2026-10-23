r"""local record aliased"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ assigns self.x
    def setx(self, v: int) -> None:
        self.x = v


_g = C(0)


#@ ensures \result == 0
def probe() -> int:
    c = C(0)
    d = c
    d.setx(5)
    return c.x

if __name__ == "__main__":
    print("CPython:", probe())
