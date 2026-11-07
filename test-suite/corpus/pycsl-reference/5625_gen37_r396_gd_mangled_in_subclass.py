r"""Test 5625 -- gen #37 route #396 (expected FAIL): `getattr(r, "_S__k", 0)` with `S(R)` storing `self.__k`; PROVED at base 3b2d2e763 (CPython 5). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING).
"""
# pycsl-expected: FAIL
class R:
    def __init__(self) -> None:
        self.x: int = 1


class S(R):
    def __init__(self) -> None:
        super().__init__()
        self.__k: int = 5


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "_S__k", 0)


if __name__ == "__main__":
    try:
        print("result", f(S()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
