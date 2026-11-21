"""Test 1077 — ROUTE #48 negative witness (b): a seeded `OrderedDict` drops its pairs.

FALSE OF THE PROGRAM: `OrderedDict([(1, 5)])[1]` is 5 in Python, so `f()` returns 0.

The same defect through a different constructor, and it is here for the reason witness 1054
is in route #42 and 1071 in route #47: a fix keyed on one constructor would have been the
same mistake one name later. At the parent commit 57777b56 `\\result == 7` PROVED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import OrderedDict


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    d = OrderedDict([(1, 5)])
    if d[1] == 0:
        return 7
    return 0
