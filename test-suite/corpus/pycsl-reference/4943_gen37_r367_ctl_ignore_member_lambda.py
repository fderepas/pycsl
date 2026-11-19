r"""Test 4943 -- gen #37 route #367 (expected PASS): CONTROL: `_ignore_` of a helper name, `member(2)`, a lambda attribute: `C(1)`, `C(2)`, `C.A` prove (CPython ok).
"""
# pycsl-expected: PASS
from enum import Enum, member

class C(Enum):
    _ignore_ = ["tmp"]
    tmp = 7
    A = 1
    B = member(2)
    f = lambda self: 0

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    x = C(1)
    y = C(2)
    z = C.A
    return 0

if __name__ == "__main__":
    print(f())
