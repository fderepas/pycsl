r"""G29 IE-G2 — a module-global method with a handled placeholder read, inlined into a claiming caller."""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    def f(self) -> int:
        xs: List[int] = []
        try:
            v = xs[0]
        except IndexError:
            return 9
        return v * 0


_g = C()


#@ ensures \result == 0
def probe() -> int:
    return _g.f()


if __name__ == "__main__":
    print("CPython:", probe())
