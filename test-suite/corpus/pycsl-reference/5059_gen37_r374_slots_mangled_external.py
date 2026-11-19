r"""Test 5059 -- gen #37 route #374 (expected FAIL): `a.__x = 2` outside any class is NOT mangled (`__x`), the slot is `_A__x`: AttributeError, PROVED at base. REFUSED now.
"""
# pycsl-expected: FAIL
class A:
    __slots__ = ("__x",)
    def __init__(self) -> None:
        self.__x = 1

#@ no_exception \all
def f(a: A) -> int:
    a.__x = 2
    return 0

if __name__ == "__main__":
    print(f(A()))
