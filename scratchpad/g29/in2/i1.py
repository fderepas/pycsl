r"""global inliner: early return inside callee branch"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 0

    def f(self, v: int) -> int:
        if v > 0:
            return 1
        return 2


_g = C()


#@ ensures \result == 2
def probe() -> int:
    return _g.f(5)


if __name__ == "__main__":
    print("CPython:", probe())
