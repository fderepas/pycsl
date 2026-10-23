r"""global field record aliased to local"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ assigns self.x
    def setx(self, v: int) -> None:
        self.x = v


_g = C(0)


class D:
    def __init__(self) -> None:
        self.c = C(0)


_d = D()


#@ ensures \result == 0
def probe() -> int:
    a = _d.c.x
    c = _d.c
    c.x = a + 5
    return _d.c.x - a

if __name__ == "__main__":
    print("CPython:", probe())
