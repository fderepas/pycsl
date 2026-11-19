# lvV: parameter named `hashlib`; the user sha256 MUTATES the object; claim its field unchanged.
from __future__ import annotations
import hashlib


class D:
    #@ assigns \nothing
    def __init__(self, n: int) -> None:
        self.n: int = n

    #@ assigns \nothing
    def hexdigest(self) -> str:
        return "x"


class K:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.c: int = 0

    #@ assigns self.c
    def sha256(self, b: bytes) -> D:
        self.c = self.c + 1
        return D(self.c)


#@ ensures hashlib.c == \old(hashlib.c)
def dig(hashlib: K, s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    k = K()
    dig(k, "abc")
    print("VIOLATION contract" if k.c != 0 else "result", k.c)
