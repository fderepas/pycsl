from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    return Path(s) == Path(s)


def g() -> None:
    import builtins
    globals().update(Path=lambda s: object())


if __name__ == "__main__":
    g()
    print("result", f("a"))
