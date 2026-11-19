r"""Test 2943 — gen #36 r272 (expected FAIL): a FRESH receiver `C().chk(k)`, raising undeclared, under `no_exception \all` PROVED at
5fe6cbdd; CPython raises ValueError for `m(1)`.
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
def m(k: int) -> int:
    C().chk(k)
    return 7


if __name__ == "__main__":
    try:
        m(1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
