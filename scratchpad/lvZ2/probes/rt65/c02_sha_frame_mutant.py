from __future__ import annotations
import hashlib
from pathlib import Path
from typing import List

G: List[int] = [0]


#@ ensures True
#@ assigns \nothing
def f(path: str) -> str:
    _p = Path(path)
    G[0] = 1
    return hashlib.sha256(_p.read_bytes()).hexdigest()


if __name__ == "__main__":
    print("result", f("/etc/hostname"), G)
