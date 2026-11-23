r"""Test 10438 -- run #9 u71, review rt79 z1, route #627 (FAIL, PRE-EXISTING). The first --import-path entry
is a ZIP archive holding zh38.py (returns 2), the second a directory holding zh38.py with `ensures \result
== 1`. pycsl probes path entries only as directories, so it read the second one; CPython's zipimport loads
the archive's module: `cd <tree root> && PYTHONPATH=test-suite/corpus/pycsl-reference/multi_file_lib/u71z/
lib.zip:test-suite/corpus/pycsl-reference/multi_file_lib/u71y python <this file>` prints "result 2". Base
c115e0a5a and u69 73f47db9d PROVED the claim below. REFUSED: PYCSL-SEM-IMPORT-PATH-NOT-DIRECTORY (every
--import-path entry must be an existing directory).
"""
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/u71z/lib.zip --import-path test-suite/corpus/pycsl-reference/multi_file_lib/u71y
# pycsl-expected: FAIL
from zh38 import one


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return one()


if __name__ == "__main__":
    print("result", g())
