r"""Test 6557 -- route #435 (expected FAIL): red team 34 witness `c0_str_unbound_bytes` (getting-better/open-routes/witnesses-r435/c0_str_unbound_bytes.py). PROVED at base 78b519f63; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: bytes) -> int:
    s = str.upper(x)
    return 0


if __name__ == "__main__":
    try:
        r = f(b"a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
