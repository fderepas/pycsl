"""Test 1106 — ROUTE #55 CONTROL, the LIST spelling was DECIDED TRUE and deleted the empty branch.

FALSE OF THE PROGRAM: `o.probe([])` returns 0 in Python — an empty dict is falsy.

Found by following the 27th plane's own NAMED FOLLOW-UP. `bin/check-type-keyed-constant-
answers.py` justifies this arm with a claim about the CONTRACTS rather than about the
lowering — "sound for the type-safety+frame contracts the mirror carries, because deleting a
branch cannot make an `ensures True` false" — and records that NOTHING CHECKS that claim.
A real postcondition breaks it. At the parent commit `d8bde948` the emitted body was

    if true then begin raise (Return 7) end else begin raise (Return 0) end

so the arm Python takes was UNREACHABLE and `\result == 7` was proved over a STRICT SUBSET
of the reachable states. Routes #50/#51's sentence at a different type and a different
connective: DECIDED FROM A TYPE where only a value fact could justify it.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self, d: List[int]) -> int:
        if d:
            return 7
        return 0


if __name__ == "__main__":
    o = C()
    assert o.probe([]) == 0
