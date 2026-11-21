r"""Test 2945 — gen #36 r272 (expected FAIL): a CHAIN `m -> self.mid -> self.chk`: `mid` has no raise of its own (nothing to
declare), `chk` raises undeclared; `m` claims `no_exception \all`. PROVED at 5fe6cbdd; CPython
raises ValueError for `C().m(1)`.
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
    def mid(self, k: int) -> int:
        return self.chk(k)

    #@ ensures \result == 7
    #@ assigns \nothing
    #@ no_exception \all
    def m(self, k: int) -> int:
        self.mid(k)
        return 7


if __name__ == "__main__":
    try:
        C().m(1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
