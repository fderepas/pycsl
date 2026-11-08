r"""Test 6563 -- route #435 (expected FAIL): red team 34 witness `c15_bytes_lower_str` (getting-better/open-routes/witnesses-r435/c15_bytes_lower_str.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: str) -> int:
    s = bytes.lower(x)
    return 0


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
