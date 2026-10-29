r"""Test 6964 -- route #450 (expected FAIL): `super().v` reads an INSTANCE field set by the base `__init__` (not visible through super). PROVED on main db6c57253 (red team 36 witness `c5_s006_super_field.py`); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE / PYCSL-R450-SUPER-UNRESOLVED).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.v = 1


class Q(B):
    def g(self) -> int:
        return super().v


#@ no_exception \all
def f(p: Q) -> int:
    return p.g()


if __name__ == "__main__":
    try:
        r = f(Q())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
