r"""Test 4110 -- gen #37 route #318 (expected FAIL): `n = 2; for i in range(n): n = 5` re-read the stop each iteration; `\result == 5` PROVED (CPython 2). The stop is now captured once before the loop.
"""
# pycsl-expected: FAIL
#@ ensures \result == 5
def f() -> int:
    n = 2
    c = 0
    #@ loop invariant 0 <= i <= 5
    #@ loop invariant c == i
    #@ loop variant 6 - i
    #@ loop invariant c == 0 ==> n == 2
    #@ loop invariant c > 0 ==> n == 5
    for i in range(n):
        n = 5
        c += 1
    return c

if __name__ == "__main__":
    assert f() == 5, f()
