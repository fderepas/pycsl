"""1142 — ROUTE #60 POSITIVE CONTROL: LISTS are untouched by the repair.

The route is dict-only — a list tracks its length in a sidecar ref, and `a[i] = v` really
does leave `len(a)` alone. This must keep proving, or the repair has over-reached from
dicts into the list model.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1]
    xs.append(2)
    return len(xs)
