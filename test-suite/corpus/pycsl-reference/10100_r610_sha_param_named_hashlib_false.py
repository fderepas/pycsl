r"""Test 10100 -- route #610 (rt61 M1, expected FAIL): a PARAMETER named `hashlib` whose `sha256(..)` is a user method with an effect (a counter): `hashlib.sha256(..).hexdigest()` is NOT the module's digest, so the two digests differ in CPython while the deterministic model would prove them equal. The model of the module call
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
