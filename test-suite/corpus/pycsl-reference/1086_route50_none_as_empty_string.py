"""Test 1086 — ROUTE #50 negative witness (b): `None` WAS THE EMPTY STRING.

FALSE OF THE PROGRAM: `None == ""` is False in Python, so `m(-1, "x")` returns 0.

The twin of 1085 and the other half of the same defect: a `None` bound to a str-typed local
emitted `s := ""`, so a later `s == ""` was decidably TRUE. The emitter already knew this
was wrong where it had built a real carrier — `statements.py`'s `iropt_str` local says in
so many words that `""` "cannot be told apart from a genuinely EMPTY string" and uses
`IrSNone` — and this is the residue that carrier does not cover. At 90fed0c9 `\\result == 7`
PROVED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires c < 0
    #@ requires t == "x"
    #@ ensures \result == 7
    def m(self, c: int, t: str) -> int:
        s = t
        s = None
        if c > 0:
            s = t
        if s == "":
            return 7
        return 0


if __name__ == "__main__":
    o = C()
    assert o.m(-1, "x") == 0
