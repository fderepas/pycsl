r"""Test 6581 -- route #435 (expected PASS): CONTROL: `str.upper(s)` (s: str), `bytes.upper(b)` (b: bytes), `str.lower("AB")`, `int.bit_length(n)` (n: int) under `no_exception \all` (CPython ok). PROVED at candidate.
"""
# pycsl-expected: PASS
#@ no_exception \all
def f(s: str, b: bytes, n: int) -> int:
    x = str.upper(s)
    y = bytes.upper(b)
    z = str.lower("AB")
    k = int.bit_length(n)
    return 0


if __name__ == "__main__":
    print("result", f("a", b"a", 5))
