r"""Test 10089 -- lvV law-free sha-256 model (expected FAIL): `.encode()` on a `Path` raises
AttributeError in CPython, which the model does not raise, so it is REFUSED
(`PYCSL-R7V-SHA-RECEIVER`) rather than lowered as a `str` encode.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == 1
#@ assigns \nothing
def enc(p: Path) -> int:
    try:
        h = hashlib.sha256(p.encode()).hexdigest()
        return 1
    except UnicodeEncodeError:
        return 1


if __name__ == "__main__":
    try:
        r = enc(Path("x"))
        print("result", r)
    except AttributeError as e:
        print("VIOLATION contract", e)
