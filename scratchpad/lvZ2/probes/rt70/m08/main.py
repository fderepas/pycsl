from __future__ import annotations
import h

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = h.mk(s)
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
