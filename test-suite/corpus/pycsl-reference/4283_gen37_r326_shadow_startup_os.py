r"""Test 4283 -- gen #37 route #326 (expected FAIL): a local `os.py` shadowing the startup-loaded `os`: PROVED `os.getpid() == 7`. REFUSED: PYCSL-SEM-IMPORT-SHADOWS-STDLIB.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r326shadow
import os

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    return os.getpid()

if __name__ == "__main__":
    assert f() == 7, f()
