r"""Test 2948 — gen #36 r272 (expected FAIL): the fresh-receiver form drops a DECLARED `#@ raises` too: `C().chk(k)` with
`raises ValueError when k > 0` PROVED `no_exception \all` at 5fe6cbdd; CPython raises ValueError.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns \nothing
    #@ raises ValueError when k > 0
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
