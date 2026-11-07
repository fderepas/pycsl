r"""Test 6965 -- route #450 (expected FAIL): `super().k()` in `R(Q(B))`, no class after R binds `k`. PROVED on main db6c57253 (red team 36 witness `c5_s008_super_two_level.py`); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE / PYCSL-R450-SUPER-UNRESOLVED).
"""
# pycsl-expected: FAIL
class B:
    def h(self) -> int:
        return 1


class Q(B):
    def m(self) -> int:
        return 2


class R(Q):
    def g(self) -> int:
        return super().k()


#@ no_exception \all
def f(p: R) -> int:
    return p.g()


if __name__ == "__main__":
    try:
        r = f(R())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
