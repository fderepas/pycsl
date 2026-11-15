from __future__ import annotations
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(a: Any, n: int) -> int:
    x = 0
    try:
        if n > 100:
            raise TypeError("u")
        x = 1
        y = a + 1
    except TypeError:
        return x
    return 0


if __name__ == "__main__":
    r = f("s", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
