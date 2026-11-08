r"""Test 2947 — gen #36 r272 (expected FAIL): the static form drops even a DECLARED `#@ raises`: the route #100/#105/#186 wrap is
keyed on `self.`/typed-variable receivers, so `C.chk(k)` with `raises ValueError when k > 0`
PROVED `no_exception \all` at 5fe6cbdd; CPython raises ValueError for `m(1)`.
"""
# pycsl-expected: FAIL
class C:
    #@ ensures \result == 0
    #@ raises ValueError when k > 0
    @staticmethod
    def chk(k: int) -> int:
        if k > 0:
            raise ValueError("bad")
        return 0


#@ ensures \result == 7
#@ no_exception \all
def m(k: int) -> int:
    C.chk(k)
    return 7


if __name__ == "__main__":
    try:
        m(1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
