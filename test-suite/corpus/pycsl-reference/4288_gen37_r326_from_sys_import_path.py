r"""Test 4288 -- gen #37 route #326 (expected FAIL): the same `sys.path` edit through `from sys import path as _p`. REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r326main
from sys import path as _p
import os
_p.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "multi_file_lib", "r326alt"))
from r326sp import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 2, g()
