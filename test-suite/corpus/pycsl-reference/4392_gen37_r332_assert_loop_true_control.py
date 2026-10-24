r"""Test 4392 -- gen #37 route #332 (expected PASS): CONTROL: a TRUE `assert s < 3` inside a `while` body under `no_exception \all` PROVES from the loop invariant.
"""
# pycsl-expected: PASS
#@ ensures \result == 3
#@ assigns \nothing
#@ no_exception \all
def g() -> int:
    s = 0
    i = 0
    #@ loop invariant 0 <= i <= 3 and s == i
    #@ loop variant 3 - i
    while i < 3:
        assert s < 3
        s = s + 1
        i = i + 1
    return s

if __name__ == "__main__":
    try:
        print(g())
    except AssertionError:
        print("CPython raises AssertionError")
