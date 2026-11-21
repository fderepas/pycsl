from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == 1
#@ assigns \nothing
def f(path: str) -> int:
    try:
        _p = Path(path)
        hashlib.sha256(_p.read_bytes()).hexdigest()
    except OSError:
        return 0
    except ValueError:
        return 2
    return 1


if __name__ == "__main__":
    print("result", f("/nonexistent"))
