r"""Test 8302 -- route #519 (control, expected PASS): conversions and arithmetic at DECLARED kinds stay field initialisers: `str` of a `str` parameter, `n * m` and `n ** 2` over `int` parameters, a literal power `2 ** 3`; CPython f(2, 3, "a") returns 1
"""
# pycsl-expected: PASS


class C:
    def __init__(self, n: int, m: int, name: str) -> None:
        self.label = str(name)
        self.area = n * m
        self.sq = n ** 2
        self.eight = 2 ** 3


#@ no_exception \all
#@ ensures \result == 1
def f(n: int, m: int, name: str) -> int:
    c = C(n, m, name)
    return 1


if __name__ == "__main__":
    print(f(2, 3, "a"))
