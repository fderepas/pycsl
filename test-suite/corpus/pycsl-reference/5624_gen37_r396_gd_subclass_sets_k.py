r"""Test 5624 -- gen #37 route #396 (expected FAIL): `getattr(r, "k", 0) == 0` for `r: R` while a subclass `S(R)` stores `self.k = 5`; PROVED at base 3b2d2e763 (CPython 5). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING: the subclass closure binds `k`).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1


class S(R):
    def __init__(self) -> None:
        super().__init__()
        self.k: int = 5


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    try:
        print("result", f(S()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
