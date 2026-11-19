r"""Test 5550 -- gen #37 route #392 (expected FAIL): `from collections import UserList` + a `class UserList` LOCAL to a def + module `class D(UserList)` hashed by `{d}` (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-S1-UNMODELLED-BASE: the base resolves by scope to the import).
"""
# pycsl-expected: FAIL
from collections import UserList


def _unused() -> int:
    class UserList:
        pass
    return 0


class D(UserList):
    pass


#@ no_exception \all
def f(d: D) -> int:
    s = {d}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(D())
        print("no violation", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
