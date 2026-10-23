r"""Test 1691 - ROUTE #197 carrier (gen #30): `getattr(o, "a", 0)` on an object of UNKNOWN static type answered the DEFAULT, and the body read it. `bin/check-getattr-erasure.py` held this UNKNOWN bucket at a RATCHET rather than calling it safe, and said why: the default is "a GUESS ... Not demonstrated to be exploitable - a contract cannot name a field of an object whose type the model does not carry - but it is not sound by argument either". THE CONTRACT DOES NOT HAVE TO NAME THE FIELD: the BODY reads it and the contract reads `\result`. This emitted `let v = ref 0 in v := 0;` with `o` UNUSED (Why3 warns so) and PROVED `\result == 1`, while CPython answers 2 for any object with `a = 7`. The UNKNOWN case now answers a PER-SITE opaque - route #47's own device, hashed on the call's IR so two reads of the same expression agree - while ABSENT keeps the faithful default.
"""
# pycsl-expected: FAIL
from typing import Any

_ = 0  # anchor


class C:
    def __init__(self):
        self.a: int = 7


#@ requires True
#@ ensures \result == 1
def peek(o: Any) -> int:
    v = getattr(o, "a", 0)
    if v == 0:
        return 1
    return 2
