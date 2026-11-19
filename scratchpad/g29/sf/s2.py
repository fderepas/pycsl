r"""self counter increment twice"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1
    def inc(self) -> None:
        self.n = self.n + 1


#@ ensures \result == 1
def probe() -> int:
    c = C()
    c.inc()
    c.inc()
    return c.n


if __name__ == "__main__":
    print("CPython:", probe())
