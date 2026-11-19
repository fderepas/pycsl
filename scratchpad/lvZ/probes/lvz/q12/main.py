from __future__ import annotations
from h import Box


#@ ensures \result == True
def f(s: str) -> bool:
    b = Box(1)
    p = b.mk(s)
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
