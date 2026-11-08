"""Test 1219 — ROUTE #85's COMPLETENESS GAIN, AND THE POSITIVE WITNESS THAT BOUNDS THE REPAIR.

This is the TRUE twin of 1216. Before the repair it was REFUSED while the FALSE claim proved;
after it, the field carries `map_update_some (const (None: option int)) 1 5` — the same
faithful chain a LOCAL dict literal has always produced — and this TRUE claim PROVES.

**WHY A POSITIVE WITNESS IS REQUIRED HERE AND NOT OPTIONAL.** Every expected-FAIL witness in
this family asserts that something must NOT prove, and an OVER-BROAD repair — one that made
every dict field unconstrained — would satisfy ALL of them at once while destroying the
capability. Only a file that must STILL PROVE can fail when the guard grows too wide. Routes
#83 and #79 carry the same instrument (witnesses 1211 and 1215).

It also records the campaign's standing preference: route #82 was closed by a FAITHFUL capture
and became a completeness gain; routes #79, #83 and #86 could not be, because the value is
genuinely not recoverable at the site. **PREFER FAITHFUL WHEREVER THE INFORMATION EXISTS.**
Here it exists — the literal is right there in the source — so an unconstrained value would
have been a needless loss.

A GENUINELY EMPTY literal (`self.d = {}`) is also still faithful and keeps `const None`; that
is what makes this repair a fix rather than a blanket erasure of dict fields.
"""
from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


class E:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {}


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    if 1 in c.d:
        return 1
    return 0


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    e = E()
    if 1 in e.d:
        return 1
    return 0
