# lvV: a LOCAL named `hashlib` shadows the module inside the function.
# needs: v07h.py
from __future__ import annotations
import hashlib
from v07h import K


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    hashlib = K()
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    r = same("abc")
    print("VIOLATION contract" if r is not True else "result", r)
