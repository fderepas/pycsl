r"""Test 5551 -- gen #37 route #392 (expected FAIL): the same with `UserDict` (D defines `__init__` + `super().__init__()`) (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-S1-UNMODELLED-BASE).
"""
# pycsl-expected: FAIL
from collections import UserDict


def _unused() -> int:
    class UserDict:
        pass
    return 0


class D(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self.x: int = 1


#@ no_exception \all
def f(d: D) -> int:
    s = {d}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
