r"""Test 5065 -- gen #37 route #374 (expected FAIL): class `_A` mangles `__x` to `_A__x` (leading underscores stripped); B stores `self._A__x` (a real slot) and `self.__x` (`_B__x`, AttributeError). REFUSED (the `_A__x` store alone is admitted, control 5091).
"""
# pycsl-expected: FAIL
class _A:
    __slots__ = ("__x",)
    def __init__(self) -> None:
        self.__x = 1

class B(_A):
    __slots__ = ()
    def __init__(self) -> None:
        super().__init__()
        self._A__x = 2
        self.__x = 3

#@ no_exception \all
def f() -> int:
    b = B()
    return 0

if __name__ == "__main__":
    print(f())
