r"""Test 9522 -- lvP cap-vm-unerase-tuple (expected PASS): CONTROL for the arity gate. The declared element
is a PAIR but one append pushes a TRIPLE (CPython accepts it: the annotation is not enforced). The tuple
model is NOT applied to such a local (every append must be a display of the element's arity), so the
function keeps the base lowering -- an `array int` of erased elements -- and the true `\length` claim
proves exactly as at base (no new refusal, no typed tuple claimed for a triple).
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List, Tuple


def mutable_state(cls): return cls


@mutable_state
class B:
    #@ ensures \length(\result) == 2
    #@ assigns \nothing
    def build(self, n: str, e: "ExprIR") -> List[Tuple[str, "ExprIR"]]:
        rules = []
        rules.append((n, e))
        rules.append((n, e, n))
        return rules


if __name__ == "__main__":
    r = B().build("a", 1)
    print("VIOLATION" if len(r) != 2 else "result", r)
