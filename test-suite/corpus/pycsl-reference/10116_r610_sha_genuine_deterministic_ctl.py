r"""Test 10116 -- route #610 CONTROL (expected PASS): a GENUINE `hashlib.sha256(..).hexdigest()` keeps lvV's deterministic digest model: two digests of the same bytes are equal.
"""
# pycsl-expected: PASS
from __future__ import annotations
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    try:
        return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()
    except UnicodeEncodeError:
        return True


if __name__ == "__main__":
    print("result", same("abc"))
