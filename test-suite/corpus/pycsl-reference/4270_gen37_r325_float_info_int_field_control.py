r"""Test 4270 -- gen #37 route #325 control (expected PASS): an INT field of `sys.float_info` keeps its int model.
"""
# pycsl-expected: PASS
import sys
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if sys.float_info.dig % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1
