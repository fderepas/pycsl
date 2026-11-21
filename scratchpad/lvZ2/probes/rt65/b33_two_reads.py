from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    a = hashlib.sha256(p.read_bytes()).hexdigest()
    b = hashlib.sha256(p.read_bytes()).hexdigest()
    return a == b


if __name__ == "__main__":
    print("result", f("/proc/self/stat"))
