from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == "x"
#@ assigns \nothing
def f(path: str) -> str:
    _p = Path(path)
    return hashlib.sha256(_p.read_bytes()).hexdigest()


if __name__ == "__main__":
    print("result", f("/etc/hostname"))
