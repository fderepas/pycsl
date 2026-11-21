r"""Test 10087 -- lvV law-free sha-256 model (expected PASS): the digest READS its input: equal
strings give equal digests (an input-blind facade could not prove this for two parameters).
"""
# pycsl-expected: PASS
from __future__ import annotations
import hashlib


#@ requires a == b
#@ ensures \result == True
#@ assigns \nothing
def eq(a: str, b: str) -> bool:
    return hashlib.sha256(a.encode()).hexdigest() == hashlib.sha256(b.encode()).hexdigest()


if __name__ == "__main__":
    r = eq("x", "x")
    print("VIOLATION contract" if r is not True else "result", r)
