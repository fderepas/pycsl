r"""Test 3903 -- gen #37 route #307 (expected FAIL): `(x := 5) + x` read `x` before the walrus; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe q16_walrus_lhs).
"""
# pycsl-expected: FAIL
#@ ensures \result == 5
def f() -> int:
    x = 0
    y = (x := 5) + x
    return y

if __name__ == "__main__":
    assert f() == 5
