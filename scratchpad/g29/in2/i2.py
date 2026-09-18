r"""global inliner: callee loop with return"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 0

    def f(self) -> int:
        for i in range(3):
            if i == 1:
                return i
        return 9


_g = C()


#@ ensures \result == 9
def probe() -> int:
    return _g.f()


if __name__ == "__main__":
    print("CPython:", probe())
