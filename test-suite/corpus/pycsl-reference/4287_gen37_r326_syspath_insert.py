r"""Test 4287 -- gen #37 route #326 (expected FAIL): `sys.path.insert(0, .../r326alt)` makes CPython import `r326alt/r326sp.py` (f = 1) while pycsl resolved the `--import-path` copy (f = 2) and PROVED `g() == 2`. REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r326main
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "multi_file_lib", "r326alt"))
from r326sp import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 2, g()
