r"""Test 4388 -- gen #37 route #332 (expected FAIL): a failing `assert i == 5` reading a `for` target AFTER its loop under `no_exception \all` PROVED (CPython raises AssertionError). The loop-target analyses now count the read; FAILS.
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g() -> int:
    i = 0
    for i in range(3):
        pass
    assert i == 5
    return 7

if __name__ == "__main__":
    # CPython ground truth: this call RAISES (see the docstring); no handler, because a
    # handler that can catch AssertionError around an assert is refused (route 16).
    print(g())
