r"""Test 4380 -- gen #37 route #332 (expected FAIL): `x = 1; assert x == 2; return 7` under `no_exception \all` PROVED (CPython raises AssertionError). The assert is now an obligation under `\all`; FAILS on `no_exception: AssertionError reachable`.
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g() -> int:
    x = 1
    assert x == 2
    return 7

if __name__ == "__main__":
    try:
        print(g())
    except (AssertionError, IndexError) as e:
        print("CPython raises", type(e).__name__)
