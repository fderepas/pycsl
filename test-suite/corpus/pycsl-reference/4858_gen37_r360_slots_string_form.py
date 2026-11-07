r"""Test 4858 -- gen #37 route #360 (expected FAIL): (new) single-string `__slots__ = "x"` (ONE slot named x), `__init__` stores `self.y`. REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
class R:
    __slots__ = "x"
    def __init__(self) -> None:
        self.x = 0
        self.y = 0

#@ no_exception \all
def f() -> int:
    r = R()
    return r.x

if __name__ == "__main__":
    print(f())
