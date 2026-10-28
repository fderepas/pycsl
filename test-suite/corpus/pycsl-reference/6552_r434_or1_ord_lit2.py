r"""Test 6552 -- route #434 (expected FAIL): red team 34 witness `or1_ord_lit2` (getting-better/open-routes/witnesses-r434/or1_ord_lit2.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str) -> int:
    return ord("ab")


if __name__ == "__main__":
    try:
        r = f("")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
