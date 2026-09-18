r"""G29 GL-H10 — inlined method with a comprehension variable named like a caller local."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self, n: int) -> int:
        ys = [i * 2 for i in range(n)]
        return len(ys)


_g = C(0)


#@ ensures \result == 2
def probe() -> int:
    i = 7
    _g.f(2)
    return i


if __name__ == "__main__":
    print("CPython:", probe())
