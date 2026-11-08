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
    # CPython ground truth: this call RAISES (see the docstring); no handler, because a
    # handler that can catch AssertionError around an assert is refused (route 16).
    print(g())
