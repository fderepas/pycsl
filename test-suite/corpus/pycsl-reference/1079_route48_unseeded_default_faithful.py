"""Test 1079 — ROUTE #48 control: the UNSEEDED forms answer 0 for a missing key, and that
is FAITHFUL — it must keep proving.

TRUE OF THE PROGRAM: an empty `Counter` and a `defaultdict(int)` both answer 0 for a key
they do not hold, so Python returns 7.

This is the half of route #48 that must NOT be touched, and it is why the fix keys on the
SEED rather than on the constructor name. `pycsl-reference/0498` already covers the
`defaultdict(int)` write-then-read cycle; this driver covers the READ of an absent key on
BOTH unseeded constructors, so a future change that made the whole dict-family opaque would
go red here instead of quietly losing a faithful model.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import Counter, defaultdict


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = Counter()
    d = defaultdict(int)
    if c[1] == 0 and d[9] == 0:
        return 7
    return 0
