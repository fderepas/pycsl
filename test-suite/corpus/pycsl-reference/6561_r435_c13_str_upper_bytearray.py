r"""Test 6561 -- route #435 (expected FAIL): red team 34 witness `c13_str_upper_bytearray` (getting-better/open-routes/witnesses-r435/c13_str_upper_bytearray.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: bytearray) -> int:
    s = str.upper(x)
    return 0


if __name__ == "__main__":
    try:
        r = f(bytearray(b"a"))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
