r"""Test 10145 -- lvX `Path(<str>)` model (expected PASS): the `_sha256_file` shape
(`_p = Path(s)`; `hashlib.sha256(_p.read_bytes()).hexdigest()`) under an OSError handler: both
arms are reachable and the result is 0 or 1 (CPython: 1 for a readable file, 0 otherwise).
"""
# pycsl-expected: PASS
from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def readable(s: str) -> int:
    _p = Path(s)
    try:
        hashlib.sha256(_p.read_bytes()).hexdigest()
        return 1
    except OSError:
        return 0


if __name__ == "__main__":
    r = readable("/nonexistent/lvx-10145")
    print("VIOLATION contract" if r not in (0, 1) else "result", r)
