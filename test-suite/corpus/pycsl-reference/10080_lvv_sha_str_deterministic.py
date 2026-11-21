r"""Test 10080 -- lvV law-free sha-256 model (expected PASS): the digest is a deterministic function
of the encoded string, so two digests of the SAME `str` are equal (CPython: always).
"""
# pycsl-expected: PASS
from __future__ import annotations
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    r = same("abc")
    print("VIOLATION contract" if r is not True else "result", r)
