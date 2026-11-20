from __future__ import annotations
import pathlib

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = pathlib.Path(s)
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
