r"""Test 6554 -- route #434 (expected FAIL): red team 34 witness `or4_ord_upper_sz` (getting-better/open-routes/witnesses-r434/or4_ord_upper_sz.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str) -> int:
    return ord(s.upper())


if __name__ == "__main__":
    try:
        r = f("\xdf")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
