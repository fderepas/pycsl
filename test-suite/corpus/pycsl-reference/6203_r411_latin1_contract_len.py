r"""Test 6203 -- route #411 (expected FAIL): `requires s == "\u00e9"`, `ensures \result == True` over `len(s) > 1` (CPython False; PROVED at base 77b33f239).
"""
# pycsl-expected: FAIL
#@ requires s == "é"
#@ ensures \result == True
def f(s: str) -> bool:
    return len(s) > 1


if __name__ == "__main__":
    try:
        r = f('é')
        if not (r == True):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
