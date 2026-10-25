r"""Test 4933 -- gen #37 route #367 (expected FAIL): `X = nonmember(3)`; `C(3)` (CPython ValueError: not a member). REFUSED (route #367: a nonmember value is not a member value).
"""
# pycsl-expected: FAIL
from enum import Enum, nonmember

class C(Enum):
    A = 1
    X = nonmember(3)

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(3)
    return 0

if __name__ == "__main__":
    print(f())
