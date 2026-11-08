r"""Test 4293 -- gen #37 route #326 (expected PASS): CONTROL: the idempotent `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` (the script directory, already pycsl's first root) is not refused; the local module's contract PROVES (CPython agrees).
"""
# pycsl-expected: PASS
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multi_file_lib.r326smod import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 2, g()
