"""1144 — ROUTE #61 POSITIVE CONTROL: the ELEMENT fold must stay faithful.

Route #61 removes only the SIZE fold for non-constant keys. The element read is a different
mechanism — the map is faithful, later entry winning — so `d[a]` with `a == b` must keep
proving CPython's answer of 2. Without this control, a repair that refused every
non-constant-key dict literal outright would satisfy 1143 and nothing would notice.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires a == b
#@ ensures \result == 2
#@ assigns \nothing
def f(a: int, b: int) -> int:
    d: Dict[int, int] = {a: 1, b: 2}
    return d[a]
