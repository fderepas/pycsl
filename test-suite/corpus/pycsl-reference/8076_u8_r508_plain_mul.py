r"""Test 8076 -- route #508 (expected FAIL: a Why3 type error at base (real vs int), now REFUSED by name PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED): the PLAIN statement `w = n * 1.5` under `no_exception \all` -- the int -> float promotion owes |n| <= DBL_MAX and no lowering states it; CPython f(10**400) raises OverflowError
"""
# pycsl-expected: FAIL

#@ no_exception \all
def f(n: int) -> int:
    w = n * 1.5
    return 1


if __name__ == "__main__":
    try:
        r = f(10**400)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
