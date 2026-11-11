r"""Test 9512 -- lvP cap-vm-unerase-tuple (expected FAIL): false twin of 9511. The loop binds `nm` to the
appended name `n`, so `#@ assert nm == "zz"` must NOT prove (CPython: `nm` is "r1").
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple


def mutable_state(cls): return cls


@mutable_state
class B:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def build(self, n: str, e: "ExprIR") -> List[Tuple[str, "ExprIR"]]:
        rules = []
        rules.append((n, e))
        for nm, ex in rules:
            #@ assert nm == "zz"
            pass
        return rules


if __name__ == "__main__":
    r = B().build("r1", 7)
    print("VIOLATION assert" if r[0][0] != "zz" else "result", r)
