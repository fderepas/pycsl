r"""Test 6553 -- route #434 (expected FAIL): red team 34 witness `or2_ord_slice` (getting-better/open-routes/witnesses-r434/or2_ord_slice.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str) -> int:
    return ord(s[0:2])


if __name__ == "__main__":
    try:
        r = f("abc")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
