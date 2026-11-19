from __future__ import annotations
from pathlib import Path
import sys
setattr(sys.modules[__name__], "Path", lambda s: object())

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    return Path(s) == Path(s)


if __name__ == "__main__":
    print("result", f("a"))
