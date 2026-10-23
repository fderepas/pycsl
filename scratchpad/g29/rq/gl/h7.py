r"""G29 GL-H7 — inlined method has a for-loop over a tuple target named like a caller local."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self, d: int) -> int:
        s = 0
        for i in range(d):
            s = s + i
        return s


_g = C(0)


#@ ensures \result == 7
def probe() -> int:
    i = 7
    _g.f(3)
    return i


if __name__ == "__main__":
    print("CPython:", probe())
