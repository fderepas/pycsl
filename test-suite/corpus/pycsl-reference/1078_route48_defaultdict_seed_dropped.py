"""Test 1078 — ROUTE #48 negative witness (c): `defaultdict`'s SECOND argument is a seed,
and it was dropped too.

FALSE OF THE PROGRAM: `defaultdict(int, {1: 5})[1]` is 5 in Python, so `f()` returns 0.

This is the witness that fixes the ARGUMENT POSITION, which is the whole subtlety of route
#48: `defaultdict`'s FIRST argument is a FACTORY and dropping it is right (its missing-key
default really is 0, which is what the empty-map model gives), while its SECOND is a SEED
and dropping that is this route. A fix that refused the whole constructor would have broken
the factory form; a fix that kept it whole would have left this. At the parent commit
57777b56 `\\result == 7` PROVED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import defaultdict


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    d = defaultdict(int, {1: 5})
    if d[1] == 0:
        return 7
    return 0
