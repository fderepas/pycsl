r"""Test 4282 -- gen #37 route #326 (expected FAIL): a local `time.py` shadowing the BUILT-IN `time` module: PROVED `time.monotonic_ns() == 7`. REFUSED: PYCSL-SEM-IMPORT-SHADOWS-STDLIB.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r326shadow
import time

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    return time.monotonic_ns()

if __name__ == "__main__":
    assert f() == 7, f()
