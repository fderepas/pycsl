r"""Test 4203 -- gen #37 route #322 (expected PASS): CONTROL: `abs(7) == 7` still folds and proves.
"""
# pycsl-expected: PASS
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if abs(7) == 7:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
