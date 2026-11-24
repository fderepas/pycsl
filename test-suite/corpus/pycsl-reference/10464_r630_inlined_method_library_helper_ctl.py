r"""Test 10464 -- run #9 u72, route #630 (PASS control). As 10456 with the TRUE claim: the inlined `obj.m()`
calls qi72's own helper (1), not the program's (2); `g() == 1` proves, CPython agrees.
"""
# pycsl-expected: PASS
from qi72 import C


#@ ensures \result == 2
#@ assigns \nothing
def helper() -> int:
    return 2


obj = C()


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return obj.m()


if __name__ == "__main__":
    assert g() == 1
