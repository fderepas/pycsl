r"""Test 4289 -- gen #37 route #326 (expected FAIL): the `sys.path` edit through `_s = sys; _s.path.insert(...)` (the module object used as a value). REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r326main
import sys
import os
_s = sys
_s.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "multi_file_lib", "r326alt"))
from r326sp import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 2, g()
