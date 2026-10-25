r"""Test 4853 -- gen #37 route #360 (expected FAIL): witness s06: `__slots__ = ("a",)`, `__init__(v)` stores `self.b = v`; PROVED (CPython AttributeError). REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
class R:
    __slots__ = ("a",)
    def __init__(self, v: int) -> None:
        self.a = v
        self.b = v

#@ no_exception \all
#@ ensures \result == 3
def f() -> int:
    r = R(3)
    return r.a

if __name__ == "__main__":
    print(f())
