r"""Test 2944 — gen #36 r272 (expected FAIL): a FIELD receiver `self.d.chk(k)`, raising undeclared, under `no_exception \all`
(CPython raises ValueError for `C(D()).m(1)`).
"""
# pycsl-expected: FAIL
class D:
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns \nothing
    def chk(self, k: int) -> int:
        if k > 0:
            raise ValueError("bad")
        return 0


class C:
    def __init__(self, d: D) -> None:
        self.d: D = d

    #@ ensures \result == 7
    #@ assigns \nothing
    #@ no_exception \all
    def m(self, k: int) -> int:
        self.d.chk(k)
        return 7


if __name__ == "__main__":
    try:
        C(D()).m(1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
