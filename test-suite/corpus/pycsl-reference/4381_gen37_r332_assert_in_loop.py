r"""Test 4381 -- gen #37 route #332 (expected FAIL): a failing `assert s < 2` inside a `while` body (third iteration) under `no_exception \all` PROVED (CPython raises AssertionError). FAILS on the AssertionError obligation.
"""
# pycsl-expected: FAIL
#@ ensures \result == 3
#@ assigns \nothing
#@ no_exception \all
def g() -> int:
    s = 0
    i = 0
    #@ loop invariant 0 <= i <= 3 and s == i
    #@ loop variant 3 - i
    while i < 3:
        assert s < 2
        s = s + 1
        i = i + 1
    return s

if __name__ == "__main__":
    # CPython ground truth: this call RAISES (see the docstring); no handler, because a
    # handler that can catch AssertionError around an assert is refused (route 16).
    print(g())
