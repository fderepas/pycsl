r"""Test 4280 -- gen #37 route #326 (expected FAIL): a local `math.py` (on an `--import-path` root) shadowing the stdlib name made `math.floor(3) == 4` PROVE; CPython never loads it (3). REFUSED: PYCSL-SEM-IMPORT-SHADOWS-STDLIB.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r326shadow
import math

#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return math.floor(3)

if __name__ == "__main__":
    assert f() == 4, f()
