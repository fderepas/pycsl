r"""Test 5420 -- gen #37 systematic rule S1 / route #381 (expected FAIL): red team 29 `h01_userlist` -- `class D(UserList)` (a standard-library base the model has no entry for) hashed under `no_exception`; PROVED at base 7bf752d4e (CPython TypeError). REFUSED (PYCSL-S1-UNMODELLED-BASE).
"""
# pycsl-expected: FAIL
from collections import UserList

class D(UserList):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
