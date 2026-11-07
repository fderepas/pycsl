r"""Test 5348 -- gen #37 route #382 (expected FAIL): `d: UserList`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from collections import UserList

#@ no_exception \all
#@ ensures \result == 1
def g(d: UserList) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(UserList()))
