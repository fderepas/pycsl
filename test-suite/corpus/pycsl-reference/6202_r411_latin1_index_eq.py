r"""Test 6202 -- route #411 (expected FAIL): `ensures \result == False` over `t[0] == "\u00e9"` for `t = "\u00e9"` (CPython True; PROVED at base 77b33f239).
"""
# pycsl-expected: FAIL
#@ ensures \result == False
def f() -> bool:
    t = "é"
    return t[0] == "é"


if __name__ == "__main__":
    try:
        r = f()
        if not (r == False):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
