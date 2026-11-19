r"""Test 10102 -- route #610 (rt61 M1, expected FAIL): a PARAMETER named `hashlib`: the user `sha256` MUTATES the object, the claim says its field is unchanged. The model of the module call
applies only when the head name is the module import, bound nowhere in the function and not
rebound at module level; here it is not, so the file is REFUSED
(`PYCSL-R610-EXT-MODULE-NAME-SHADOWED`) rather than lowered as the module call.
"""
# pycsl-expected: FAIL
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
