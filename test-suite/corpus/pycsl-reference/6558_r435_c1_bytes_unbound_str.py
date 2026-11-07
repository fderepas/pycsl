r"""Test 6558 -- route #435 (expected FAIL): red team 34 witness `c1_bytes_unbound_str` (getting-better/open-routes/witnesses-r435/c1_bytes_unbound_str.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: str) -> int:
    s = bytes.upper(x)
    return 0


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
