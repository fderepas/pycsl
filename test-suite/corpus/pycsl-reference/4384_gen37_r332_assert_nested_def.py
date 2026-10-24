r"""Test 4384 -- gen #37 route #332 (expected FAIL): a failing `assert 1 == 2` in a NESTED function under `no_exception \all` PROVED (CPython raises AssertionError). FAILS on the AssertionError obligation.
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g() -> int:
    #@ ensures \result == 7
    #@ assigns \nothing
    #@ no_exception \all
    def h() -> int:
        assert 1 == 2
        return 7
    return h()

if __name__ == "__main__":
    try:
        print(g())
    except (AssertionError, IndexError) as e:
        print("CPython raises", type(e).__name__)
