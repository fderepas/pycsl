from typing import NamedTuple
_ = 0  # anchor


class P(NamedTuple):
    x: int
    y: int


#@ ensures \result == 99
def probe() -> int:
    p = P(3, 4)
    return p.x + p.y
