r"""Test 7204 -- route #464 (expected FAIL): driver probe (cc1) -- D's claimed `get` returns `self.__x` (`_D__x`, never set); the field tables found C's `__x`. CPython raises AttributeError (private name mangling); PROVED at 33f7ac681; now FAILS (no field `_D__x` in the record).
"""
# pycsl-expected: FAIL
class C:
    #@ ensures self.__x == n
    def __init__(self, n: int) -> None:
        self.__x = n


class D(C):
    #@ ensures \result == self.__x
    def get(self) -> int:
        return self.__x


#@ ensures \result == n
def f(n: int) -> int:
    d = D(n)
    return d.get()


if __name__ == "__main__":
    print(f(3))
