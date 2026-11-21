r"""Test 6206 -- route #411 (expected FAIL): `t = "\t"; t[1]` under `no_exception \all` (CPython IndexError; PROVED at base 77b33f239: the tab literal was four characters to Z3).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f() -> str:
    t = "\t"
    return t[1]


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
