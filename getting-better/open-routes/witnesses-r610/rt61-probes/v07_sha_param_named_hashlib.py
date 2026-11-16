# lvV: a PARAMETER named `hashlib` (the guard checks only classes / imports) whose sha256(..)
# returns an object with a NON-deterministic hexdigest.
# needs: v07h.py
from __future__ import annotations
import hashlib
from v07h import K


#@ ensures \result == True
#@ assigns \nothing
def same(hashlib: K, s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    r = same(K(), "abc")
    print("VIOLATION contract" if r is not True else "result", r)
