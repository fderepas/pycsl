from __future__ import annotations
from h import mk


#@ ensures \result == True
def f(s: str) -> bool:
    p = mk(s)
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
