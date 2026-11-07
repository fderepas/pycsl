r"""Test 4204 -- gen #37 route #322 (expected PASS): CONTROL: `int(2.5)` truncates to 2 (CPython 2) and still proves.
"""
# pycsl-expected: PASS
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return int(2.5)

if __name__ == "__main__":
    assert f() == 2, f()
