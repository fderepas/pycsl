r"""Test 6963 -- route #450 (expected FAIL): `super().h(1)` over `def h(self)`. PROVED on main db6c57253 (red team 36 witness `c5_s000_super_missing_arg.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE / PYCSL-R450-SUPER-UNRESOLVED).
"""
# pycsl-expected: FAIL
class B:
    def h(self) -> int:
        return 1


class Q(B):
    def g(self) -> int:
        return super().h(1)


#@ no_exception \all
def f(p: Q) -> int:
    return p.g()


if __name__ == "__main__":
    try:
        r = f(Q())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
