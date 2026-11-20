from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return str(p).strip() == str(p).strip()


if __name__ == "__main__":
    print("result", f("a"))
