"""1155 — ROUTE #66 POSITIVE CONTROL: `del d[k]` on a PRESENT key still discharges.

The `del` obligation was WIRED, not refused — unlike `divmod`/`int(str)`, the receiver is a
real modelled map, so `Map.get d k <> None` is a faithful condition. A correct program must
still prove, which is what makes 1154 a real obligation rather than a ban on `del`.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ no_exception KeyError
#@ ensures True
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1}
    del d[1]
    return 0
