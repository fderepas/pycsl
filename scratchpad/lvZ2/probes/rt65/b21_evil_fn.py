from __future__ import annotations
from pathlib import Path


def evil() -> None:
    setattr(Path, "__eq__", lambda a, b: False)


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    return Path(s) == Path(s)


if __name__ == "__main__":
    evil()
    print("result", f("a"))
