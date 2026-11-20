from __future__ import annotations
import hashlib
from pathlib import Path

G: int = 0


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(path: str) -> str:
    global G
    _p = Path(path)
    G = G + 1
    return hashlib.sha256(_p.read_bytes()).hexdigest()


if __name__ == "__main__":
    print("result", f("/etc/hostname"), G)
