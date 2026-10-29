r"""Test 7058 -- route #460 (expected PASS): CONTROL -- an un-claimed `@property` with no raising site, read by `f` claiming `#@ no_exception \all`; PROVED at base and candidate.
"""
# pycsl-expected: PASS


class C:
    def __init__(self, n: int) -> None:
        self.n = n

    @property
    def v(self) -> int:
        return self.n + 1


#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return c.v


if __name__ == "__main__":
    print(f(2))
