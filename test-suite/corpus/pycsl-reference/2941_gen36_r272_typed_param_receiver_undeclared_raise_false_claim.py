r"""Test 2941 — gen #36 r272 (expected FAIL): the same undeclared raise through a class-typed PARAMETER receiver `c.chk(k)` under
`no_exception \all` PROVED at 5fe6cbdd; CPython raises ValueError for `m(C(), 1)`.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns \nothing
    def chk(self, k: int) -> int:
        if k > 0:
            raise ValueError("bad")
        return 0


#@ ensures \result == 7
#@ no_exception \all
def m(c: C, k: int) -> int:
    c.chk(k)
    return 7


if __name__ == "__main__":
    try:
        m(C(), 1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
