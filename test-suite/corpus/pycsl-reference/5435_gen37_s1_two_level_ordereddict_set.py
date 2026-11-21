r"""Test 5435 -- gen #37 systematic rule S1 (expected FAIL): NEW latent (not a red-team probe): `class B(OrderedDict)`, `class C(B)` and a `C` instance in a set display under `no_exception`; PROVED at base 7bf752d4e (CPython TypeError, unhashable). REFUSED (PYCSL-S1-UNMODELLED-BASE).
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
    s = {c}
    return 1

if __name__ == "__main__":
    print(f(C()))
