r"""Test 10081 -- lvV law-free sha-256 model (expected FAIL): nothing is assumed about distinct
inputs, so the `stable_hash` fold of two DISTINCT strings must NOT be provably distinct
(CPython: "k6404" and "k44509" both fold to 850588129).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import hashlib


#@ requires a != b
#@ ensures \result == True
#@ assigns \nothing
def distinct(a: str, b: str) -> bool:
    x = int(hashlib.sha256(a.encode("utf-8")).hexdigest()[:8], 16) % 2147483647
    y = int(hashlib.sha256(b.encode("utf-8")).hexdigest()[:8], 16) % 2147483647
    return x != y


if __name__ == "__main__":
    r = distinct("k6404", "k44509")
    print("VIOLATION contract" if r is not True else "result", r)
