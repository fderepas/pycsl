r"""Test 3892 -- gen #37 route #307 (expected FAIL): `x - (x := 1) + 1` ran the walrus before reading `x`; Why3 evaluates application arguments right-to-left, Python left-to-right. PROVED before #307 (red-team probe g06b_walrus_rtl).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
def f() -> int:
    x = 0
    return x - (x := 1) + 1

if __name__ == "__main__":
    assert f() == 1
