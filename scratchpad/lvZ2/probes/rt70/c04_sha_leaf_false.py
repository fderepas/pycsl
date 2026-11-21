from __future__ import annotations
import hashlib
from pathlib import Path


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(path: str) -> str:
    _p = Path(path)
    r = hashlib.sha256(_p.read_bytes()).hexdigest()
    #@ assert False
    return r


if __name__ == "__main__":
    print("result", f("/etc/hostname"))
