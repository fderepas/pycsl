from __future__ import annotations
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int, Err: Any) -> int:
    x = 0
    try:
        if n > 0:
            raise ValueError("v")
        x = 0
    except Err:
        x = 1
    return x


if __name__ == "__main__":
    r = f(1, ValueError)
    print("VIOLATION contract" if r != 0 else "result", r)
