r"""Test 2940 — gen #36 r272 (expected FAIL): `self.chk(k)` where `chk` raises ValueError for k > 0 WITHOUT `#@ raises`; `m` claims
`no_exception \all`. The method stub carried no `raises`, so it PROVED at 5fe6cbdd (CPython raises
ValueError for `C().m(1)`). Now refused (PYCSL-SEM-UNDECLARED-CALLEE-RAISE).
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
    #@ assigns \nothing
    #@ no_exception \all
    def m(self, k: int) -> int:
        self.chk(k)
        return 7


if __name__ == "__main__":
    try:
        C().m(1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
