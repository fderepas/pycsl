r"""Test 2952 — gen #36 r272 (expected PASS): controls: the undeclared raise CAUGHT around the call (`m`), and a `no_exception
KeyError` claim that the callee's ValueError does not touch (`m2`: the rule reads no
precondition, so it is the exception NAME that keeps it silent; `requires k <= 0` keeps the
promised value true on every admitted argument). Both keep PASS; CPython agrees (`m` never
raises; `m2(k <= 0)` returns 7).
"""
# pycsl-expected: PASS
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
        try:
            self.chk(k)
        except ValueError:
            return 7
        return 7

    #@ requires k <= 0
    #@ ensures \result == 7
    #@ assigns \nothing
    #@ no_exception KeyError
    def m2(self, k: int) -> int:
        self.chk(k)
        return 7


if __name__ == "__main__":
    assert C().m(1) == 7 and C().m(0) == 7
    assert C().m2(0) == 7 and C().m2(-4) == 7
