r"""Test 4882 -- gen #37 route #360: CONTROL: slotted subclass of a base WITHOUT `__slots__` (instances keep a `__dict__`); PROVES (CPython 1).
"""
class A:
    def __init__(self) -> None:
        self.x = 0

class B(A):
    __slots__ = ("y",)
    def __init__(self) -> None:
        super().__init__()
        self.y = 0
        self.z = 1

#@ no_exception \all
def f() -> int:
    b = B()
    return b.z

if __name__ == "__main__":
    print(f())
