r"""Test 4304 -- gen #37 route #327 (expected FAIL): a global `F = 0.5` read beside a parameter `f: int`: `F % 1 == 0` read the int parameter and PROVED (CPython 0.5 % 1 == 0.5); also bypassed #325. REFUSED.
"""
# pycsl-expected: FAIL
F = 0.5
#@ ensures \result == 1
#@ assigns \nothing
def g(f: int) -> int:
    if F % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g(3) == 1, g(3)
