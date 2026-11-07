r"""Test 4193 -- gen #37 route #322 (expected FAIL): `sum([0.5, 0.5]) == 0` PROVED via `sum(int(e))` (CPython 1.0).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if sum([0.5, 0.5]) == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
