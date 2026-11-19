r"""Test 5637 -- gen #37 route #397 (expected FAIL): `self.k, self.j = 5, 6`; `getattr(r, "j", 0) == 0`; PROVED at base 3b2d2e763 (CPython 6). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1
        self.k, self.j = 5, 6


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "j", 0)


if __name__ == "__main__":
    try:
        print("result", f(R()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
