r"""Test 7205 -- route #464 (expected PASS): CONTROL -- a private field `self.__x` written and read inside its own class C, claimed in C's method contracts (the claim is mangled by its anchor's class like the body). CPython raises nothing; PROVED at base and candidate.
"""
# pycsl-expected: PASS
class C:
    #@ ensures self.__x == n
    def __init__(self, n: int) -> None:
        self.__x = n

    #@ ensures \result == self.__x
    def get(self) -> int:
        return self.__x


#@ ensures \result == n
def f(n: int) -> int:
    c = C(n)
    return c.get()


if __name__ == "__main__":
    assert f(3) == 3
