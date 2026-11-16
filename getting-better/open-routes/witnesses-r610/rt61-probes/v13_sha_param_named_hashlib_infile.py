# lvV: parameter named `hashlib`, classes in the SAME file (does the function-name guard catch it?).
from __future__ import annotations
import hashlib


class D:
    #@ assigns \nothing
    def __init__(self, n: int) -> None:
        self.n: int = n

    #@ assigns \nothing
    def hexdigest(self) -> str:
        return str(self.n)


class K:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.c: int = 0

    #@ assigns self.c
    def sha256(self, b: bytes) -> D:
        self.c = self.c + 1
        return D(self.c)


#@ ensures \result == True
#@ assigns \nothing
def same(hashlib: K, s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    r = same(K(), "abc")
    print("VIOLATION contract" if r is not True else "result", r)
