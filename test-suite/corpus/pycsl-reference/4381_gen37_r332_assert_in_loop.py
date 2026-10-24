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
    try:
        print(g())
    except (AssertionError, IndexError) as e:
        print("CPython raises", type(e).__name__)
