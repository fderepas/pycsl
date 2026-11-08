r"""Test 6604 -- route #438 (expected FAIL): red team 34 w04: `{t if c else ()}` with `t: tuple`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(t: tuple, c: bool) -> int:
    s = {t if c else ()}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(([1],), True)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
