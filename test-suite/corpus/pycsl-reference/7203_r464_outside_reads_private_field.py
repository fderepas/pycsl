r"""Test 7203 -- route #464 (expected FAIL): driver probe (cc1) -- `c.__x` outside any class reads `__x`; C's `__init__` stores `_C__x`. CPython raises AttributeError (private name mangling); PROVED at 33f7ac681; now REFUSED by route #445 over the mangled names.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self, n: int) -> None:
        self.__x = n


#@ ensures \result == n
#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return c.__x


if __name__ == "__main__":
    print(f(3))
