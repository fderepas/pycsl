"""Test 1216 — ROUTE #85: a NON-EMPTY dict literal stored to a field in `__init__` was
modelled as the EMPTY MAP, and membership was then DECIDED ON.

`_field_default` answered every dict/set field with `(const (None: option int))` — a
DEFINITE value, not an unknown one — so `Map.get d k` was decidably `None`. The emitted
WhyML showed it with nothing left to infer:

    type c = { mutable d: map int (option int) }
    let f () : int ensures { (result = 0) } =
      let c = { d = (const (None: option int)) } in ...

Measured before the repair: this file's claim PROVED, where CPython returns 1. The TRUE twin
(1219) was refused — the asymmetry that makes this a route and not imprecision.

**A LOCAL dict literal was ALWAYS lowered faithfully**, to a `map_update_some (const (None:
option int)) k v` chain. Only the FIELD arm dropped the contents. So the information exists,
and the repair is a FAITHFUL CAPTURE rather than an unconstrained value — route #82's rule —
which is why 1219 now PROVES and this is a completeness GAIN as well as a soundness fix.

This file is `pycsl-expected: FAIL`: the claim is FALSE of the program and must not prove.
"""
# pycsl-expected: FAIL
from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    if 1 in c.d:
        return 1
    return 0
