r"""Test 5633 -- gen #37 route #397 (expected FAIL): `for self.k in range(5, 6)` in `__init__`; `getattr(r, "k", 0) == 0`; PROVED at base 3b2d2e763 (CPython 5). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING: every Store-context attribute binds).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1
        for self.k in range(5, 6):
            pass


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    try:
        print("result", f(R()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
