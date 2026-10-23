r"""global inliner: keyword call"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 0

    def f(self, a: int, b: int) -> int:
        return a - b


_g = C()


#@ ensures \result == 1
def probe() -> int:
    return _g.f(b=1, a=2) * 0 + (2 - 1) * 0 + _g.f(b=2, a=1)


if __name__ == "__main__":
    print("CPython:", probe())
