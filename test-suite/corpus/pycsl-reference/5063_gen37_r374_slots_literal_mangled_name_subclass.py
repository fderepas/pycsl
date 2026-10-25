r"""Test 5063 -- gen #37 route #374 (expected FAIL): A declares the literal slot `_A__x`; subclass B stores `self.__x` (`_B__x`); AttributeError (red-team s23). REFUSED.
"""
# pycsl-expected: FAIL
class A:
    __slots__ = ("_A__x",)
    def __init__(self) -> None:
        self.__x = 1

class B(A):
    __slots__ = ()
    def __init__(self) -> None:
        super().__init__()
        self.__x = 2

#@ no_exception \all
def f() -> int:
    b = B()
    return 0

if __name__ == "__main__":
    print(f())
