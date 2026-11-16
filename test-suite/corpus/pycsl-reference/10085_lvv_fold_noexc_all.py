r"""Test 10085 -- lvV law-free sha-256 model (expected FAIL): the `stable_hash` fold raises
UnicodeEncodeError (a lone surrogate) and, in the law-free model, `int(<digest>, 16)` may raise
ValueError; under `no_exception \all` it must NOT verify (CPython: `"\ud800"` raises).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import hashlib


#@ no_exception \all
#@ ensures \result >= 0
#@ assigns \nothing
def fold(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16) % 2147483647


if __name__ == "__main__":
    try:
        fold("\ud800")
        print("result ok")
    except UnicodeEncodeError as e:
        print("VIOLATION no_exception", e)
