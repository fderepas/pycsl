r"""Test 4857 -- gen #37 route #360 (expected FAIL): (new) `__slots__ = SL` (a module constant): the slot set is not read, REFUSED. REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
SL = ("x",)

class R:
    __slots__ = SL
    def __init__(self) -> None:
        self.x = 0
        self.y = 0

#@ no_exception \all
def f() -> int:
    r = R()
    return r.x

if __name__ == "__main__":
    print(f())
