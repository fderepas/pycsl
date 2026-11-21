"""Test 1218 — ROUTE #85, the SET arm: `self.s = {7}` then `7 in c.s` proved `\\result == 0`
where CPython returns 1.

A set field lowers to the same `map int (option int)` as a dict field, so it took the same
empty-map default. It is repaired DIFFERENTLY from the dict arm, and deliberately: a local set
literal is INT-ERASED by this pipeline (`s = {7}` lowers to `let s = ref 0`), so unlike the
dict case there is no faithful element lowering to reuse. The set arm therefore gets a
POLYMORPHIC UNCONSTRAINED map, which closes the route without inventing a representation.

**PREFER A FAITHFUL CAPTURE WHERE THE INFORMATION EXISTS, AND FALL BACK TO UNCONSTRAINED
WHERE IT GENUINELY DOES NOT** — this file and 1219 are the two halves of that rule measured
side by side, in the same repair.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL
from typing import Set


class C:
    s: Set[int]

    #@ assigns self.s
    def __init__(self) -> None:
        self.s = {7}


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    if 7 in c.s:
        return 1
    return 0
