r"""Test 5349 -- gen #37 route #382 (expected FAIL): `d: OrderedDict`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from collections import OrderedDict

#@ no_exception \all
#@ ensures \result == 1
def g(d: OrderedDict) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(OrderedDict()))
