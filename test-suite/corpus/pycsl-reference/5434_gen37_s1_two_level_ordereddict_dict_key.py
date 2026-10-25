r"""Test 5434 -- gen #37 systematic rule S1 (expected FAIL): NEW latent (not a red-team probe): `class B(OrderedDict)`, `class C(B)` -- the unmodelled standard-library base TWO levels up -- and a `C` instance as a dict key under `no_exception`; PROVED at base 7bf752d4e (CPython TypeError, unhashable). REFUSED (PYCSL-S1-UNMODELLED-BASE on `B`, named by `C`'s bases).
"""
# pycsl-expected: FAIL
from collections import OrderedDict

class B(OrderedDict):
    pass

class C(B):
    pass

#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def f(c: C) -> int:
    m = {c: 1}
    return 1

if __name__ == "__main__":
    print(f(C()))
