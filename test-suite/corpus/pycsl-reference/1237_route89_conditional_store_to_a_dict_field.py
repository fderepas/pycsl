"""Test 1237 — ROUTE #89 on a DICT field: the same fence gap, the same emission.

`self.d = {1: 5}` then `if k > 0: self.d = {1: 9}`, constructed as `C(0)`. Measured before the
repair: `c.d[1] == 9` PROVED, CPython returns 5. Route #85's faithful `map_update_some` chain
is built from the nested store's literal, unconditionally.

Kept as a SEPARATE witness from the list carrier (1236) deliberately: routes #85 and #87 are
two different captures reached through two different arms of `_field_default`, and a repair
that fixed only one of them would satisfy the other witness by accident. **BOTH ARMS OR
NEITHER.**

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL
from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self, k: int) -> None:
        self.d = {1: 5}
        if k > 0:
            self.d = {1: 9}


#@ requires True
#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    c = C(0)
    return c.d[1]
