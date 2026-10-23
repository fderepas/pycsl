r"""record param mutation visible to caller"""
from typing import List
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.v = 0


#@ assigns p.v
#@ ensures p.v == \old(p.v)
def f(p: P) -> None:
    p.v = p.v + 1


#@ ensures \result == 0
def probe() -> int:
    p = P()
    f(p)
    return p.v


if __name__ == "__main__":
    print("CPython:", probe())
