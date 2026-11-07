r"""Test 6070 -- gen #37 route #415 (expected FAIL): `"%(k)s" % {"j": a}` under `no_exception \all` (CPython KeyError; PROVED at base 4431ef86f). REFUSED (PYCSL-R415-UNCHECKED-PERCENT-FORMAT).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(a: int) -> str:
    return "%(k)s" % {"j": a}


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
