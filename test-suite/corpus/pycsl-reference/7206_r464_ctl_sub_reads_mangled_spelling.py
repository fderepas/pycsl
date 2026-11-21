r"""Test 7206 -- route #464 (expected PASS): CONTROL -- subclass D reads the base's private field by its CPython name `self._C__x`. CPython raises nothing; PROVED at candidate (base did not know the field `_C__x`).
"""
# pycsl-expected: PASS
class C:
    #@ ensures self.__x == n
    def __init__(self, n: int) -> None:
        self.__x = n


class D(C):
    #@ ensures \result == self._C__x
    def get(self) -> int:
        return self._C__x


#@ ensures \result == n
def f(n: int) -> int:
    d = D(n)
    return d.get()


if __name__ == "__main__":
    assert f(3) == 3
