r"""Test 4880 -- gen #37 route #360: CONTROL: slotted `B(A)` storing only slot names (own and inherited); PROVES (CPython 2).
"""
class A:
    __slots__ = ("x",)
    def __init__(self) -> None:
        self.x = 1

class B(A):
    __slots__ = ("y",)
    def __init__(self) -> None:
        super().__init__()
        self.y = 2

#@ no_exception \all
#@ ensures \result == 2
def f() -> int:
    b = B()
    return b.y

if __name__ == "__main__":
    print(f())
