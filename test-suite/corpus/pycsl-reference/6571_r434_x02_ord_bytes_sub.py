r"""Test 6571 -- route #434 (expected FAIL): `ord(b[0])` of a `bytes` (an int: CPython TypeError) under `no_exception \all`: a non-str argument is REFUSED (`PYCSL-R434-ORD-LENGTH`). PROVED at base 78b519f63.
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ requires len(b) >= 1
def f(b: bytes) -> int:
    return ord(b[0])


if __name__ == "__main__":
    try:
        print("result", f(b"a"))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
