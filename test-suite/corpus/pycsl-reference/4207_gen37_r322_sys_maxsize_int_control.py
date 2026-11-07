r"""Test 4207 -- gen #37 route #322 (expected PASS): CONTROL: `sys.maxsize` (an int constant) is not refused; `% 1 == 0` proves.
"""
# pycsl-expected: PASS
import sys
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if sys.maxsize % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
