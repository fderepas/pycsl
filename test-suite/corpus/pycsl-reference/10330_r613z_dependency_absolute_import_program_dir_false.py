r"""Test 10330 -- run #8 u60, review rt72 A1 (FAIL, PRE-EXISTING). The program imports the package module
multi_file_lib/r613z/lib/dep.py, whose ABSOLUTE `from r613z_one import one` pycsl resolved from the
dependency's own directory (lib/r613z_one.py, `ensures \result == 1`). CPython resolves it through the
program's sys.path, whose first entry is THIS directory: `cd <tree root> && python <this file>` loads
./r613z_one.py and prints "result 2". pycsl PROVED `\result == 1` at int73.
REFUSED: PYCSL-SEM-IMPORT-DEPENDENCY-SEARCH-ORDER.
"""
# pycsl-expected: FAIL
from multi_file_lib.r613z.lib.dep import f


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()


if __name__ == "__main__":
    print("result", g())
