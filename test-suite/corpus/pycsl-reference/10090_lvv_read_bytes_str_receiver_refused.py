r"""Test 10090 -- lvV law-free sha-256 model (expected FAIL): `.read_bytes()` on a `str` raises
AttributeError in CPython, which the model does not raise, so a receiver the source does not show
is a `pathlib.Path` is REFUSED (`PYCSL-R7V-SHA-RECEIVER`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == 1
#@ assigns \nothing
def rb(p: str) -> int:
    try:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        return 1
    except OSError:
        return 1


if __name__ == "__main__":
    try:
        r = rb("x")
        print("result", r)
    except AttributeError as e:
        print("VIOLATION contract", e)
