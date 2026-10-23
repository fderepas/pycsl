"""1154 — ROUTE #66 NEGATIVE: `del d[k]` on an ABSENT key under `no_exception KeyError`.

CPython raises `KeyError: 5`. The operation lowers FAITHFULLY (`d := map_update_none !d 5`)
and simply carried no exception obligation — there was no trigger row for `DelSubscript` at
all. Proved before the row was wired; must never prove again.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ no_exception KeyError
#@ ensures True
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1}
    del d[5]
    return 0
