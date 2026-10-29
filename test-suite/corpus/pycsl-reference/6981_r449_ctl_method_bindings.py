r"""Test 6981 -- route #449 (expected PASS): CONTROL: `self.m(..)` with a default left out and given by keyword, and a `@staticmethod` through its class (by position and by keyword), each callee with an `ensures`, under `#@ no_exception \all`. Admitted; PROVED at base and candidate (CPython ok).
"""
# pycsl-expected: PASS
class C:
    #@ ensures \result == a + b
    def m(self, a: int, b: int = 1) -> int:
        return a + b

    #@ ensures \result == 2 * a
    @staticmethod
    def dbl(a: int) -> int:
        return 2 * a

    #@ no_exception \all
    #@ ensures \result == 2 * n + 3
    def k(self, n: int) -> int:
        return self.m(n) + self.m(n, b=2)


#@ no_exception \all
#@ ensures \result == 2 * n + 2
def f(n: int) -> int:
    return C.dbl(n) + C.dbl(a=1)


if __name__ == "__main__":
    c = C()
    print(c.k(2), f(2))
