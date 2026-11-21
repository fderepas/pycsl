r"""Test 5060 -- gen #37 route #374 (expected FAIL): B(A) slotted, B stores `self.__x` (`_B__x`) beside its real slot `y`; PROVED at base (AttributeError). REFUSED now.
"""
# pycsl-expected: FAIL
class A:
    __slots__ = ("__x",)

class B(A):
    __slots__ = ("y",)
    def __init__(self) -> None:
        self.y = 0
        self.__x = 1

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    b = B()
    return b.y

if __name__ == "__main__":
    print(f())
