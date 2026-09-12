"""Test 1212 — ROUTE #79: an `__init__` field initialiser whose RHS names anything OUTSIDE
the parameter set silently became a literal `0`.

`_collect_init_construction` captured a field initialiser only when its RHS mentioned
`__init__` parameters AND NOTHING ELSE. Everything else was omitted, and at the allocation
site `_field_default` supplied `rec_info['defaults'].get(fn, 0)` — **a literal `0`** —
because `__init__` is never emitted as a function at all: it is INLINED as a record literal.

The comment guarding the omission called it *"sound, just less precise"*. **It is not less
precise, it is WRONG.** "Less precise" is an unconstrained value; a literal `0` is a
definite false fact, and the emitter then proves postconditions from it.

Measured at HEAD, before the repair:

    class C:
        n: int
        def __init__(self, items: List[int]) -> None:
            self.n = len(items)

    C([1,2,3]).n        #@ ensures \\result == 0     <-- PROVED; CPython returns 3

FOUR CARRIERS, one erasure site, four different reasons the RHS left the capture shape:

    a BUILTIN            `self.n = len(items)`     \\result == 0  CPython 3  PROVED
    a MODULE CONSTANT    `self.x = K + 1`          \\result == 0  CPython 9  PROVED
    ANOTHER SELF FIELD   `self.b = self.a + 1`     \\result == 0  CPython 6  PROVED
    a PARAMETERLESS `__init__` (see 1214's note)   \\result == 0  CPython 9  PROVED

THE TRUE TWIN WAS REFUSED IN EVERY CASE, which is the asymmetry that makes this a route and
not merely imprecision: the model asserted a value it had no grounds for, and refused the
value the program actually computes.

THE REPAIR EMITS AN UNCONSTRAINED VALUE, NOT A REFUSAL. A blanket refusal was scoped FIRST
and REFUTED BY MEASUREMENT before a line was written — see 1215 for the bound that survives.

This file is `pycsl-expected: FAIL`: the claim is FALSE of the program and must not prove.
"""
# pycsl-expected: FAIL
from typing import List


class C:
    n: int

    #@ assigns self.n
    def __init__(self, items: List[int]) -> None:
        self.n = len(items)


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C([1, 2, 3])
    return c.n
