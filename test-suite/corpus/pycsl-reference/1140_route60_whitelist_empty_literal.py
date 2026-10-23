"""1140 — ROUTE #60 POSITIVE CONTROL: the whitelist still folds.

Bound once to a top-level dict literal, one top-level store with a LITERAL key distinct
from every key already present. The emitter CAN show the post-store size, so this must
keep proving. Without this control a repair that refused every dict `len` would satisfy
all seven route #60 negatives and nothing would notice.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {}
    d[1] = 1
    return len(d)
