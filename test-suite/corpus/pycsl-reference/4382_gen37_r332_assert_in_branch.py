r"""Test 4382 -- gen #37 route #332 (expected FAIL): a failing `assert n > 5` on the `n > 0` branch under `no_exception \all` PROVED (CPython `g(1)` raises AssertionError). FAILS on the AssertionError obligation.
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g(n: int) -> int:
    if n > 0:
        assert n > 5
    return 7

if __name__ == "__main__":
    try:
        print(g(1))
    except (AssertionError, IndexError) as e:
        print("CPython raises", type(e).__name__)
