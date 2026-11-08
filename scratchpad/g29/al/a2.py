r"""global in a list literal"""
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
    a = _g.x
    cs: List[C] = [_g]
    cs[0].x = a + 5
    return _g.x - a

if __name__ == "__main__":
    print("CPython:", probe())
