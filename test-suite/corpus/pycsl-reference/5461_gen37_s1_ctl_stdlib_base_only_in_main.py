r"""Test 5461 -- gen #37 systematic rule S1 (expected PASS): CONTROL: `class D(collections.UserList)` (an unmodelled standard-library base) is named only by the `__main__` driver, which is not verified: no verified code reaches it, so S1 admits it; the verified `f` proves (CPython 3).
"""
# pycsl-expected: PASS
from collections import UserList

class D(UserList):
    pass

#@ ensures \result == x + 1
#@ assigns \nothing
def f(x: int) -> int:
    return x + 1

if __name__ == "__main__":
    d = D([1])
    assert f(2) == 3 and len(d) == 1
