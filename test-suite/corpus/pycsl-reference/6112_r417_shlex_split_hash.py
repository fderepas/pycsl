r"""Test 6112 -- route #417 (expected FAIL): `{shlex.split("a b")}` under `no_exception \all` (CPython TypeError, a list). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
import shlex


#@ no_exception \all
def f() -> int:
    s = {shlex.split("a b")}
    return 0


if __name__ == "__main__":
    try:
        print(f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
