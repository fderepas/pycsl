"""Test 1102 — ROUTE #51 PRECISION GUARD: a BOUND local keeps its decided answer.

TRUE OF THE PROGRAM: `s` is bound to a string literal in this very function and is never
`None`, so Python does NOT take the `is None` branch and `o.probe()` returns 7.

Route #51's repair narrows route #50's always-present answer to names the function BINDS.
This file is the other side of that narrowing and is why it is a narrowing rather than a
retreat: `s` IS bound here, by a literal, so the model may still DECIDE `s is None` false
and the contract must still prove. A repair that made every string `is None` opaque would
lose this, and nothing else in the corpus would notice.
"""
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self) -> int:
        s = "x"
        if s is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    assert o.probe() == 7
