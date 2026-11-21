r"""G29 GL-H9 — inlined method loops with a tuple target named like a caller local."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self, xs: List[int]) -> int:
        s = 0
        for i, v in enumerate(xs):
            s = s + v
        return s


_g = C(0)


#@ ensures \result == 1
def probe() -> int:
    i = 7
    _g.f([1, 2])
    return i


if __name__ == "__main__":
    print("CPython:", probe())
