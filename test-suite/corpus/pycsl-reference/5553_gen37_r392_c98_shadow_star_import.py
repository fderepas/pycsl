r"""Test 5553 -- gen #37 route #392 (expected FAIL): `from collections import *` + a nested `class OrderedDict` + module `class D(OrderedDict)` (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-S1-UNMODELLED-BASE: the name is the star import's).
"""
# pycsl-expected: FAIL
from collections import *


def _unused() -> int:
    class OrderedDict:
        pass
    return 0


class D(OrderedDict):
    pass


#@ no_exception \all
def f(d: D) -> int:
    s = {d}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
