r"""Test 4852 -- gen #37 route #360 (expected FAIL): witness s05: `__slots__ = ()`, `__init__` stores `self.x`; PROVED (CPython AttributeError). REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
class R:
    __slots__ = ()
    def __init__(self) -> None:
        self.x = 0

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    r = R()
    return r.x

if __name__ == "__main__":
    print(f())
