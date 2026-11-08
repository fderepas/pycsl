r"""Test 6562 -- route #435 (expected FAIL): red team 34 witness `c14_bytes_upper_bytearray` (getting-better/open-routes/witnesses-r435/c14_bytes_upper_bytearray.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: bytearray) -> int:
    s = bytes.upper(x)
    return 0


if __name__ == "__main__":
    try:
        r = f(bytearray(b"a"))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
