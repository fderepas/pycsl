from __future__ import annotations
from pathlib import Path
from typing import Optional, TypeAlias

MaybeP: TypeAlias = Optional[Path]


#@ ensures \result == True
def f(p: MaybeP) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(Path("a")))
