r"""Test 10086 -- lvV law-free sha-256 model (expected PASS): the `stable_hash` fold is in
[0, 2147483647) whatever the digest is (Python `%` by a positive modulus), with the escaping
UnicodeEncodeError / ValueError declared by the summary.
"""
# pycsl-expected: PASS
from __future__ import annotations
import hashlib


#@ ensures 0 <= \result and \result < 2147483647
#@ assigns \nothing
def fold(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:8], 16) % 2147483647


if __name__ == "__main__":
    r = fold("abc")
    print("VIOLATION contract" if not (0 <= r < 2147483647) else "result", r)
