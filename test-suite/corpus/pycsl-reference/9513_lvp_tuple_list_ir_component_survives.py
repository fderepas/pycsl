r"""Test 9513 -- lvP cap-vm-unerase-tuple (expected PASS): the SECOND (IR-node) component survives the
append: `for nm, ex in rules` binds `ex` to the appended `e`, so `#@ assert ex == e` proves. Twin: 9514.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List, Tuple


def mutable_state(cls): return cls


@mutable_state
class B:
    #@ assigns \nothing
    def build(self, n: str, e: "ExprIR", f: "ExprIR") -> List[Tuple[str, "ExprIR"]]:
        rules = []
        rules.append((n, e))
        for nm, ex in rules:
            #@ assert ex == e
            pass
        rules.append((n, f))
        return rules


if __name__ == "__main__":
    r = B().build("r1", 7, 8)
    print("VIOLATION" if r[0][1] != 7 else "result", r)
