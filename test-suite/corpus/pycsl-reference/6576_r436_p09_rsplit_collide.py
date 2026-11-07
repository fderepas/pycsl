r"""Test 6576 -- route #436 (expected FAIL): `s.rsplit(" ", n)` admitted by route #161 because a file class defines `rsplit`; n = 10**20 (CPython OverflowError): owes the ssize_t bound and FAILS. PROVED at base 78b519f63.
"""
# pycsl-expected: FAIL
class C:
    def rsplit(self, a: str, n: int) -> int:
        return n


#@ no_exception \all
def f(s: str, n: int) -> int:
    return len(s.rsplit(" ", n))


if __name__ == "__main__":
    try:
        print("result", f("a b", 10**20))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
