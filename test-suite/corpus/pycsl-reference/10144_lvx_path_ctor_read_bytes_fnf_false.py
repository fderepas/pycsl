r"""Test 10144 -- lvX `Path(<str>)` model (expected FAIL): a path built by `Path(<str>)` reaches
lvV's open-world `read_bytes` (inside `hashlib.sha256(..).hexdigest()`), which raises the OSError
family, so the FileNotFoundError handler is reachable and `\result == 1` must NOT prove (CPython: a
missing file returns 0).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == 1
#@ assigns \nothing
def file_ok(s: str) -> int:
    _p = Path(s)
    try:
        hashlib.sha256(_p.read_bytes()).hexdigest()
        return 1
    except FileNotFoundError:
        return 0


if __name__ == "__main__":
    r = file_ok("/nonexistent/lvx-10144")
    print("VIOLATION contract" if r != 1 else "result", r)
