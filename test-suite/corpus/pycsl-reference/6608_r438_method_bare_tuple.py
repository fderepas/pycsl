r"""Test 6608 -- route #438 (expected FAIL): red team 34 w11: a method hashing its parameter `t: tuple`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
class C:
    #@ no_exception \all
    def m(self, t: tuple) -> int:
        s = {t}
        return len(s)


if __name__ == "__main__":
    try:
        r = C().m(([1],))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
