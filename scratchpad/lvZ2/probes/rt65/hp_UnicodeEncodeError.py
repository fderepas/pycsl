from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == 1
#@ assigns \nothing
def f(p: Path) -> int:
    try:
        hashlib.sha256(p.read_bytes()).hexdigest()
        return 1
    except UnicodeEncodeError:
        return 0


if __name__ == "__main__":
    print("result", f(Path("\ud800")))
