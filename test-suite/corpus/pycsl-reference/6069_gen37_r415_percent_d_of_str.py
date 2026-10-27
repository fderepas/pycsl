r"""Test 6069 -- gen #37 route #415 (expected FAIL): `"%d" % s` with `s: str` under `no_exception \all` (CPython TypeError; PROVED at base 4431ef86f). REFUSED (PYCSL-R415-UNCHECKED-PERCENT-FORMAT).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str) -> str:
    return "%d" % s


if __name__ == "__main__":
    try:
        r = f('a')
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
