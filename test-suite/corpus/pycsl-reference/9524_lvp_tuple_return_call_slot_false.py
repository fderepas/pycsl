r"""Test 9524 -- lvP cap-vm-unerase-tuple (expected FAIL): false twin of 9523: the first slot is `n`, so `\result[0] == "zz"` must NOT prove (CPython: "c").
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple


def mutable_state(cls): return cls


@mutable_state
class B:
    #@ sibling_concrete
    #@ requires True
    #@ ensures \result == n
    #@ assigns \nothing
    def name_of(self, n: str) -> str:
        return n

    #@ requires True
    #@ ensures \result[0] == "zz"
    #@ assigns \nothing
    def variant(self, n: str, k: int) -> Tuple[str, List[str]]:
        c = self.name_of(n)
        types: List[str] = []
        if k > 0:
            types.append("int")
        return (c, types)


if __name__ == "__main__":
    r = B().variant("c", 1)
    print("VIOLATION contract" if r[0] != "zz" else "result", r)
