r"""Test 5058 -- gen #37 route #374 (expected FAIL): `__slots__ = ("__x",)` in A is the slot `_A__x`; `self.__x = 1` in subclass B stores `_B__x` (no `__dict__`): CPython AttributeError, PROVED under `no_exception \all` at base. REFUSED now (PYCSL-R360-SLOTS-STORE after mangling).
"""
# pycsl-expected: FAIL
class A:
    __slots__ = ("__x",)

class B(A):
    __slots__ = ()
    def __init__(self) -> None:
        self.__x = 1

#@ no_exception \all
def f() -> int:
    b = B()
    return 0

if __name__ == "__main__":
    print(f())
