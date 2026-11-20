from __future__ import annotations
from pathlib import Path
from typing import cast

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = cast(str, Path(s))
    return q == str(q)


if __name__ == "__main__":
    print("result", f("a"))
