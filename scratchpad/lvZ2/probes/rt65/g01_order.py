from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str, t: str) -> bool:
    p = Path(s)
    q = Path(t)
    return (p < q) == (str(p) < str(q))


if __name__ == "__main__":
    print("result", f("a/b", "a-b"))
