r"""Test 4854 -- gen #37 route #360 (expected FAIL): witness s08: list-form `__slots__ = ["x"]`, `__init__` stores `self.y`; PROVED (CPython AttributeError). REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
class R:
    __slots__ = ["x"]
    def __init__(self) -> None:
        self.x = 0
        self.y = 0

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    r = R()
    return r.x

if __name__ == "__main__":
    print(f())
