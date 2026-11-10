r"""Test 9511 -- lvP cap-vm-unerase-tuple (expected PASS): a `-> List[Tuple[str, "ExprIR"]]` method's
accumulator `rules.append((n, e))` is a `seq (string, emit_ir)` of native Why3 tuples, and a `for nm, ex in
rules` loop binds `nm` to the element's FIRST component, so `#@ assert nm == n` proves. At base the element was
`(any int)` and `nm` an `any int` havoc (a type error against the `str` parameter). Twin: 9512 (must FAIL).
"""
# pycsl-expected: PASS
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
            #@ assert nm == n
            pass
        return rules


if __name__ == "__main__":
    r = B().build("r1", 7)
    print("VIOLATION" if r[0][0] != "r1" else "result", r)
