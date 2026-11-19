from __future__ import annotations
import pathlib as Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
