r"""Test 4600 -- gen #37 route #339 (expected PASS): CONTROL: a plain `Enum` member bound, aliased, compared with `==` and read as `.value` is still admitted and proves.
"""
# pycsl-expected: PASS
from enum import Enum

class C(Enum):
    A = 1
    B = 2

#@ ensures \result == True
def f() -> bool:
    x = C.A
    y = x
    if x.value == 7:
        return y == x
    return y == x

if __name__ == "__main__":
    assert f() == True
