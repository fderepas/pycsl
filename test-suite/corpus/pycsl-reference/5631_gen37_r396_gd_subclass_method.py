r"""Test 5631 -- gen #37 route #396 (expected FAIL): `S(R)` defines a method `k`; `getattr(r, "k", None) is None`; PROVED at base 3b2d2e763 (CPython: a bound method). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1


class S(R):
    def k(self) -> int:
        return 5


#@ ensures \result == 0
def f(r: R) -> int:
    return 0 if getattr(r, "k", None) is None else 1


if __name__ == "__main__":
    try:
        print("result", f(S()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
