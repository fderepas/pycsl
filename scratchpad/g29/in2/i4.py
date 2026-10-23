r"""global inliner: callee param default"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 0

    def f(self, v: int = 7) -> int:
        return v


_g = C()


#@ ensures \result == 0
def probe() -> int:
    return _g.f()


if __name__ == "__main__":
    print("CPython:", probe())
