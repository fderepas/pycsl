r"""Test 4113 -- gen #37 route #318 (expected FAIL): `n = 3; for j in range(n): n = 1` re-read the shrinking stop; `\result == 1` PROVED (CPython 3). Stop captured once.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
def f() -> int:
    c = 0
    n = 3
    #@ loop invariant 0 <= j <= 1
    #@ loop invariant c == j
    #@ loop invariant c == 0 ==> n == 3
    #@ loop invariant c > 0 ==> n == 1
    #@ loop variant 3 - j
    for j in range(n):
        n = 1
        c += 1
    return c

if __name__ == "__main__":
    assert f() == 1, f()
