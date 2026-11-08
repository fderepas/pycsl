r"""Test 6555 -- route #434 (expected FAIL): red team 34 witness `or6_ord_strip` (getting-better/open-routes/witnesses-r434/or6_ord_strip.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str) -> int:
    return ord(s.strip())


if __name__ == "__main__":
    try:
        r = f(" ab ")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
