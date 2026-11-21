r"""Test 6962 -- route #450 (expected FAIL): `super().m()` where no base binds `m`; the caller `f` claims `#@ no_exception \all`. PROVED on main db6c57253 (red team 36 witness `c3_b080_super_missing.py`); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE / PYCSL-R450-SUPER-UNRESOLVED).
"""
# pycsl-expected: FAIL
class B:
    def h(self) -> int:
        return 1


class Q(B):
    def g(self) -> int:
        return super().m()


#@ no_exception \all
def f(p: Q) -> int:
    return p.g()


if __name__ == "__main__":
    try:
        r = f(Q())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
