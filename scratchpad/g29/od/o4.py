r"""same record passed twice"""
from typing import List
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.v = 0


#@ assigns p.v
#@ ensures q.v == \old(q.v)
def f(p: P, q: P) -> None:
    p.v = 5


#@ ensures \result == 0
def probe() -> int:
    p = P()
    f(p, p)
    return p.v


if __name__ == "__main__":
    print("CPython:", probe())
