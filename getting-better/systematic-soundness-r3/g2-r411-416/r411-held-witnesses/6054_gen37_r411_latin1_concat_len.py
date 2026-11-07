r"""Test 6054 -- gen #37 route #411 (expected FAIL): `ensures \result == True` over `len("\u00e9" + s) > 2`, f("a") (CPython False; PROVED at base 4431ef86f).
"""
# pycsl-expected: FAIL
#@ ensures \result == True
def f(s: str) -> bool:
    t = "é" + s
    return len(t) > 2


if __name__ == "__main__":
    try:
        r = f('a')
        if not (r == True):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
