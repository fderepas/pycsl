r"""Test 4856 -- gen #37 route #360 (expected FAIL): (new) `setattr(self, "y", 1)` in the constructor of a slotted class. REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
class R:
    __slots__ = ("x",)
    def __init__(self) -> None:
        self.x = 0
        setattr(self, "y", 1)

#@ no_exception \all
def f() -> int:
    r = R()
    return r.x

if __name__ == "__main__":
    print(f())
