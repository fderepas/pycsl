r"""Test 4115 -- gen #37 route #318 (expected PASS): CONTROL: `n = 2; for i in range(n): n = 5` runs exactly twice; `\result == 2` proves against the captured stop.
"""
# pycsl-expected: PASS
#@ ensures \result == 2
def f() -> int:
    n = 2
    c = 0
    #@ loop invariant 0 <= i <= 2
    #@ loop invariant c == i
    #@ loop variant 3 - i
    for i in range(n):
        n = 5
        c += 1
    return c

if __name__ == "__main__":
    assert f() == 2, f()
