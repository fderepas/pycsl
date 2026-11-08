r"""Test 4926 -- gen #37 route #367 (expected FAIL): `_ignore_ = NAMES` (non-literal): the member set is unknown. REFUSED now (route #367).
"""
# pycsl-expected: FAIL
from enum import Enum

NAMES = ["B"]

class C(Enum):
    _ignore_ = NAMES
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(1)
    return 0

if __name__ == "__main__":
    print(f())
