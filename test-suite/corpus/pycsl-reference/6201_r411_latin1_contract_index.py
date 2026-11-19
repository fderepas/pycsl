r"""Test 6201 -- route #411 (expected FAIL): `requires s == "\u00e9"`; `s[1]` under `no_exception \all` (CPython IndexError; PROVED at base 77b33f239).
"""
# pycsl-expected: FAIL
#@ requires s == "é"
#@ no_exception \all
def f(s: str) -> str:
    return s[1]


if __name__ == "__main__":
    try:
        r = f('é')
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
