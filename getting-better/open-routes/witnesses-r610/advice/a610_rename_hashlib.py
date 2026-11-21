# Route #610 advice followed (lvV's digest walk): "Rename that binding (e.g. `hashlib_obj`) so that
# `hashlib` names only the module." The parameter of 10102 (`hashlib: K`) renamed `hashlib_obj`:
# `hashlib_obj.sha256(..)` is now the user method, with its contract, and its effect is proved
# (CPython: 1).
# pycsl-expected: PASS
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

    #@ ensures self.c == \old(self.c) + 1
    #@ assigns self.c
    def sha256(self, b: bytes) -> D:
        self.c = self.c + 1
        return D(self.c)


#@ ensures hashlib_obj.c == \old(hashlib_obj.c) + 1
def dig(hashlib_obj: K, s: str) -> int:
    d = hashlib_obj.sha256(s.encode())
    return d.n


if __name__ == "__main__":
    k = K()
    dig(k, "abc")
    print("VIOLATION contract" if k.c != 1 else "result", k.c)
