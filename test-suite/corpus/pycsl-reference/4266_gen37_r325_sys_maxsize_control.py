r"""Test 4266 -- gen #37 route #325 control (expected PASS): `sys.maxsize` is a documented int.
"""
# pycsl-expected: PASS
import sys
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if sys.maxsize % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1
