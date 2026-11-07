r"""Test 2951 — gen #36 r272 (expected PASS): control: a DECLARED `raises ValueError when k > 0` called as `self.chk(k)` under
`requires k <= 0` + `no_exception \all` — the wrap asserts `not (k > 0)`, discharged. Keeps PASS
(CPython: no exception for k <= 0).
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns \nothing
    #@ raises ValueError when k > 0
    def chk(self, k: int) -> int:
        if k > 0:
            raise ValueError("bad")
        return 0

    #@ requires k <= 0
    #@ ensures \result == 7
    #@ assigns \nothing
    #@ no_exception \all
    def m(self, k: int) -> int:
        self.chk(k)
        return 7


if __name__ == "__main__":
    for k in (-3, 0):
        assert C().m(k) == 7
