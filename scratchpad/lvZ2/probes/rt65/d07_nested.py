from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    def g() -> bool:
        p = Path(s)
        return p == str(p)
    return g()


if __name__ == "__main__":
    print("result", f("a"))
