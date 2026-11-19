r"""Test 5590 -- gen #37 route #392 (expected PASS): CONTROL: bases resolved by SCOPE still resolve to the file class where CPython does: a module-level `class UserList` (no import) as a base, a class nested in a def whose base is a class of the SAME def, and a module `class E(object)` while a `class object` is nested elsewhere (the builtin). All hashed under `no_exception` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS


class UserList:
    pass


class D(UserList):
    pass


def _other() -> int:
    class object:
        pass
    return 0


class E(object):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(d: D, e: E) -> int:
    s = {d}
    t = {e}
    return 1


#@ no_exception \all
#@ ensures \result == 1
def g() -> int:
    class B:
        pass

    class C(B):
        pass

    c = C()
    s = {c}
    return 1


if __name__ == "__main__":
    print(f(D(), E()), g())
