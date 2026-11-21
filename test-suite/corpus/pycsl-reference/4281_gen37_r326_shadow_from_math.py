r"""Test 4281 -- gen #37 route #326 (expected FAIL): `from math import floor` through a local `math.py`: PROVED `floor(3) == 4` (CPython 3). REFUSED: PYCSL-SEM-IMPORT-SHADOWS-STDLIB.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r326shadow
from math import floor

#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return floor(3)

if __name__ == "__main__":
    assert f() == 4, f()
