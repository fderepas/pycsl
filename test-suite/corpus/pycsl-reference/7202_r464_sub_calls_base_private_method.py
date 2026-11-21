r"""Test 7202 -- route #464 (expected FAIL): driver probe (cc1) -- `self.__m()` in subclass D calls `_D__m`; C defines `_C__m`. CPython raises AttributeError (private name mangling). At 33f7ac681 refused only incidentally (`self.__m(...)` was not resolved as a method of the program at all); now REFUSED for the real reason (method admission over the mangled names: D's MRO defines no `_D__m`).
"""
# pycsl-expected: FAIL
class C:
    def __m(self) -> int:
        return 5


class D(C):
    def get(self) -> int:
        return self.__m()


#@ ensures \result == 5
#@ no_exception \all
def f(n: int) -> int:
    return D().get()


if __name__ == "__main__":
    print(f(3))
