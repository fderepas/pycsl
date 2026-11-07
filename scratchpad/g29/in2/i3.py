r"""global inliner: callee try/except return"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 0

    def f(self) -> int:
        try:
            raise ValueError()
        except ValueError:
            self.x = 4
        return self.x


_g = C()


#@ ensures \result == 0
def probe() -> int:
    return _g.f()


if __name__ == "__main__":
    print("CPython:", probe())
