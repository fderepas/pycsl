r"""Test 6959 -- route #449 (expected FAIL): `c.m(n, n)` over `def m(self, a)` on a parameter `c: C`, its result stored into an annotated local. PROVED on main db6c57253 (found while repairing); CPython raises TypeError. Now REFUSED (PYCSL-R449-CALL-SIGNATURE).
"""
# pycsl-expected: FAIL
class C:
    def m(self, a: int) -> int:
        return a


#@ no_exception \all
#@ ensures \result == n
def f(c: C, n: int) -> int:
    x: int = c.m(n, n)
    return n


if __name__ == "__main__":
    try:
        r = f(C(), 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
