r"""Test 10082 -- lvV law-free sha-256 model (expected FAIL): `<str>.encode()` raises
UnicodeEncodeError on a lone surrogate, so the handler is reachable and `\result == 1` must NOT
prove (CPython: `"\ud800"` returns 0).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import hashlib


#@ ensures \result == 1
#@ assigns \nothing
def digest_ok(s: str) -> int:
    try:
        hashlib.sha256(s.encode()).hexdigest()
        return 1
    except UnicodeEncodeError:
        return 0


if __name__ == "__main__":
    r = digest_ok("\ud800")
    print("VIOLATION contract" if r != 1 else "result", r)
