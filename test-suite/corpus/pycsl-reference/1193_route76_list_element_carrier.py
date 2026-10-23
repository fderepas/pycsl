"""1193 — ROUTE #76: the `List[<record>]` ELEMENT carrier, found by probing the repair.

The first cut of #76's guard resolved a class-typed operand only through `\\result`, a
typed local/param, and a constructor call. It MISSED the ELEMENT of a `List[<record>]`, so

    #@ ensures a[0] == a[1]

still PROVED for two distinct objects with equal fields, where CPython answers False. The
guard was extended to resolve a Subscript operand through the record-array param/field maps.

This witness exists because the gap was found by PROBING THE REPAIR FOR THE GAP IT LEAVES
rather than by waiting for the next generation to trip over it, and it is the permanent
standing check that the element carrier stays closed.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import List


class C:
    v: int

    def __init__(self, v: int) -> None:
        self.v = v


#@ requires \length(a) >= 2
#@ requires a[0].v == a[1].v
#@ ensures a[0] == a[1]
#@ assigns \nothing
def f(a: List[C]) -> int:
    return 0
