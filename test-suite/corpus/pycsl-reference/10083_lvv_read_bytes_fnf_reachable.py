r"""Test 10083 -- lvV law-free sha-256 model (expected FAIL): `<path>.read_bytes()` is an open-world
read raising the OSError family, so the FileNotFoundError handler is reachable and `\result == 1`
must NOT prove (CPython: a missing file returns 0).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == 1
#@ assigns \nothing
def file_ok(path: Path) -> int:
    try:
        hashlib.sha256(path.read_bytes()).hexdigest()
        return 1
    except FileNotFoundError:
        return 0


if __name__ == "__main__":
    r = file_ok(Path("/nonexistent/lvv-10083"))
    print("VIOLATION contract" if r != 1 else "result", r)
