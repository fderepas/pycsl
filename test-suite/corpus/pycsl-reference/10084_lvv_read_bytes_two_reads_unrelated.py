r"""Test 10084 -- lvV law-free sha-256 model (expected FAIL): two reads of the same file are
unrelated (the world can change between them: each `read_bytes()` is a fresh value), so equal
digests must NOT prove (CPython: /proc/sys/kernel/random/uuid differs on every read).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def twice(path: Path) -> bool:
    a = hashlib.sha256(path.read_bytes()).hexdigest()
    b = hashlib.sha256(path.read_bytes()).hexdigest()
    return a == b


if __name__ == "__main__":
    r = twice(Path("/proc/sys/kernel/random/uuid"))
    print("VIOLATION contract" if r is not True else "result", r)
