from __future__ import annotations
from pathlib import Path
from h import wrap


#@ ensures \result == True
def f(s: str) -> bool:
    q = wrap(Path(s))
    return q == str(Path(s))


if __name__ == "__main__":
    print("result", f("a"))
