r"""Test 6067 -- gen #37 route #414 (expected FAIL): `"ab" * n` with `0 <= n < 2**63` under `no_exception \all`, f(2**62) (CPython OverflowError "repeated string is too long": the RESULT length exceeds sys.maxsize; PROVED at base 4431ef86f).
"""
# pycsl-expected: FAIL
#@ requires 0 <= n and n < 9223372036854775808
#@ no_exception \all
def f(n: int) -> int:
    s = "ab" * n
    return 0


if __name__ == "__main__":
    try:
        r = f(2**62)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
