r"""Test 4850 -- gen #37 route #360 (expected FAIL): witness a12: `__slots__ = ("x",)`, `__init__` stores `self.y`; read `r.y` under `no_exception \all` PROVED (CPython AttributeError at construction). REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
class R:
    __slots__ = ("x",)
    def __init__(self) -> None:
        self.x = 0
        self.y = 1

#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    r = R()
    return r.y

if __name__ == "__main__":
    print(f())
