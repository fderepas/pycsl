r"""Test 5340 -- gen #37 route #381 (expected FAIL): `class D(N, UserList)` (stdlib second base), `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from collections import UserList

class N:
    pass

class D(N, UserList):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
