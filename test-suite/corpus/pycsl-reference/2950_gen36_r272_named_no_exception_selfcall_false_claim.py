r"""Test 2950 — gen #36 r272 (expected FAIL): the NAMED form: `#@ no_exception ValueError` over `self.chk(k)`, `chk` raising
ValueError undeclared. CPython raises ValueError for `C().m(1)`.
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
    #@ no_exception ValueError
    def m(self, k: int) -> int:
        self.chk(k)
        return 7


if __name__ == "__main__":
    try:
        C().m(1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
