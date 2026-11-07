r"""Test 6958 -- route #449 (expected FAIL): `self.m(n, n)` over `def m(self, a)` in a method claiming `#@ no_exception \all`. PROVED on main db6c57253 (found while repairing; the red team's instance-method probes were refused by #252 erasure, this `self` receiver was not); CPython raises TypeError. Now REFUSED (PYCSL-R449-CALL-SIGNATURE).
"""
# pycsl-expected: FAIL
class C:
    def m(self, a: int) -> int:
        return a

    #@ no_exception \all
    def k(self, n: int) -> int:
        return self.m(n, n)


if __name__ == "__main__":
    try:
        r = C().k(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
