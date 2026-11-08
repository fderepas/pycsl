r"""Test 5630 -- gen #37 route #396 (expected FAIL): `S(R)` defines a property `k`; `getattr(r, "k", 0) == 0`; PROVED at base 3b2d2e763 (CPython 5). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1


class S(R):
    @property
    def k(self) -> int:
        return 5


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    try:
        print("result", f(S()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
