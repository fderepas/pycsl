r"""Test 4773 -- gen #37 route #354 (expected PASS): CONTROL: an IntFlag member bound and compared by `is` proves (CPython True).
"""
# pycsl-expected: PASS
from enum import IntFlag

class F(IntFlag):
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == True
def f() -> bool:
    x = F.A
    y = x
    return x is y

if __name__ == "__main__":
    assert f() == True
