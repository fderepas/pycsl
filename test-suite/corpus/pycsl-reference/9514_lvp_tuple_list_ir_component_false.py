r"""Test 9514 -- lvP cap-vm-unerase-tuple (expected FAIL): false twin of 9513. Two different IR nodes `e`
and `f`; the loop's `ex` is `e`, so `#@ assert ex == f` must NOT prove (CPython: 7 != 8).
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
    def build(self, n: str, e: "ExprIR", f: "ExprIR") -> List[Tuple[str, "ExprIR"]]:
        rules = []
        rules.append((n, e))
        for nm, ex in rules:
            #@ assert ex == f
            pass
        return rules


if __name__ == "__main__":
    r = B().build("r1", 7, 8)
    print("VIOLATION assert" if r[0][1] != 8 else "result", r)
