r"""Test 4269 -- gen #37 route #325 control (expected PASS): an opaque `os.getcwd()` bound and passed to `print` stays admitted.
"""
# pycsl-expected: PASS
import os
#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    c = os.getcwd()
    print(c)
    return 3

if __name__ == "__main__":
    assert g() == 3
