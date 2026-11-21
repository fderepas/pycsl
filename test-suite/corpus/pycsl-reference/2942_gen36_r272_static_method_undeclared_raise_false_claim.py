r"""Test 2942 — gen #36 r272 (expected FAIL): a `@staticmethod` called as `C.chk(k)`, raising undeclared, under `no_exception \all`
PROVED at 5fe6cbdd; CPython raises ValueError for `m(1)`.
"""
# pycsl-expected: FAIL
class C:
    #@ ensures \result == 0
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
