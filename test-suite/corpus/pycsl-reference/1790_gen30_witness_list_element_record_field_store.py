r"""Test 1790 — WITNESS: an in-place field store on a record used as a `List[<record>]` element.

Why3 forbids a MUTABLE element inside an `array`, so a class that appears as a list element
is modelled as a PURE (immutable) record — and a field store on one cannot be made
caller-visible. Rather than emit a Why3-ill-typed `<-`, the emitter fails CLOSED and names
the rewrite (rebuild the record). One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


class Pt:
    def __init__(self, x: int) -> None:
        self.x: int = x


#@ requires \length(ps) > 0
#@ ensures \result >= 0
def bump(ps: List[Pt], p: Pt) -> int:
    p.x = 1
    return 0
