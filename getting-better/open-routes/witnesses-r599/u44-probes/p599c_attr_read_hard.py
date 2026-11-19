from __future__ import annotations
from typing import Optional


class C:
    def __init__(self, v: int) -> None:
        self.v = v


#@ ensures \result == 0
#@ assigns \nothing
def f(c: Optional[C], n: int) -> int:
    x = 0
    try:
        if n > 100:
            raise AttributeError("u")
        x = 1
        y = c.v
    except AttributeError:
        return x
    return 0


if __name__ == "__main__":
    r = f(None, 0)
    print("VIOLATION contract" if r != 0 else "result", r)
