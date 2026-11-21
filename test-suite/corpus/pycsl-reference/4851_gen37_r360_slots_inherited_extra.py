r"""Test 4851 -- gen #37 route #360 (expected FAIL): witness s02: `B(A)` both slotted (x / y), `B.__init__` stores `self.z`; PROVED (CPython AttributeError). REFUSED (PYCSL-R360-SLOTS-STORE, route #360).
"""
# pycsl-expected: FAIL
class A:
    __slots__ = ("x",)
    def __init__(self) -> None:
        self.x = 0

class B(A):
    __slots__ = ("y",)
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.z = 0

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    b = B()
    return b.y

if __name__ == "__main__":
    print(f())
