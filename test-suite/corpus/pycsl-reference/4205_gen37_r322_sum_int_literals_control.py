r"""Test 4205 -- gen #37 route #322 (expected PASS): CONTROL: `sum([1, 2, 3]) == 6` still folds.
"""
# pycsl-expected: PASS
#@ ensures \result == 6
#@ assigns \nothing
def f() -> int:
    return sum([1, 2, 3])

if __name__ == "__main__":
    assert f() == 6, f()
