r"""Test 6050 -- gen #37 route #411 (expected FAIL): `t = "\u00e9"; t[1]` under `no_exception \all` (CPython IndexError; PROVED at base 4431ef86f: the literal was emitted as its two UTF-8 bytes).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f() -> str:
    t = "é"
    return t[1]


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
