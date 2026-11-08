r"""Test 5064 -- gen #37 route #374 (expected FAIL): a dunder slot `__x__` is not mangled (store ok) but `self.__y` (`_B__y`) is outside the slots: AttributeError (red-team s24). REFUSED.
"""
# pycsl-expected: FAIL
class A:
    __slots__ = ("__x__",)

class B(A):
    __slots__ = ()
    def __init__(self) -> None:
        self.__x__ = 1
        self.__y = 1

#@ no_exception \all
def f() -> int:
    b = B()
    return 0

if __name__ == "__main__":
    print(f())
