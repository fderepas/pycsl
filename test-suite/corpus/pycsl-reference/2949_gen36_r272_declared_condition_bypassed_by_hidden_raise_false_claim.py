r"""Test 2949 — gen #36 r272 (expected FAIL): a DECLARED `raises ValueError when k < 0` on `mid` does not excuse a ValueError that
reaches `mid` through a stub (`self.chk(k)`, raising for k > 0): the caller discharges
`not (k < 0)` from `requires k >= 0` and claims `no_exception \all`. CPython raises ValueError
for `m(C(), 1)`.
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

    #@ assigns \nothing
    #@ raises ValueError when k < 0
    def mid(self, k: int) -> int:
        if k < 0:
            raise ValueError("neg")
        return self.chk(k)


#@ requires k >= 0
#@ ensures \result == 7
#@ no_exception \all
def m(c: C, k: int) -> int:
    c.mid(k)
    return 7


if __name__ == "__main__":
    try:
        m(C(), 1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
