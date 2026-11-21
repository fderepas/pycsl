r"""Test 7207 -- route #464 (expected PASS): CONTROL -- a private method `__m` called as `self.__m()` from its own class. CPython raises nothing; PROVED at base and candidate.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.k = 0

    #@ ensures \result == 5
    def __m(self) -> int:
        return 5

    #@ ensures \result == 5
    def get(self) -> int:
        return self.__m()


#@ ensures \result == 5
def f(n: int) -> int:
    c = C()
    return c.get()


if __name__ == "__main__":
    assert f(3) == 5
