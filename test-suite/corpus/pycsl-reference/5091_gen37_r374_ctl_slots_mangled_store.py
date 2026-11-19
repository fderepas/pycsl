r"""Test 5091 -- gen #37 route #374 (expected PASS): CONTROL: `self.__x` in `A` (`_A__x`), `self._A__x` and `self.__z` (`_B__z`) in B(A) are all real slots (CPython ok; the `_A__x` store was OVER-REFUSED at base).
"""
# pycsl-expected: PASS
class A:
    __slots__ = ("__x", "y")
    def __init__(self) -> None:
        self.__x = 1
        self.y = 0

class B(A):
    __slots__ = ("__z",)
    def __init__(self) -> None:
        super().__init__()
        self._A__x = 2
        self.__z = 3

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    b = B()
    return 0

if __name__ == "__main__":
    assert f() == 0
