"""1141 — ROUTE #60 POSITIVE CONTROL: distinct keys ACROSS the literal and the store.

The store key 2 is distinct from the literal's key 1 under Python's key equality, every
store is top-level, so the fold is exact and must keep proving. This is the control that
stops the whitelist from being narrowed to "empty literals only".
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1}
    d[2] = 2
    return len(d)
