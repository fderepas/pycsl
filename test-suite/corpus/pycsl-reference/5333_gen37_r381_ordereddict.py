r"""Test 5333 -- gen #37 route #381 (expected FAIL): `class D(OrderedDict)`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from collections import OrderedDict

class D(OrderedDict):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
