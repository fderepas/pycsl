r"""Test 10341 -- run #8 u61, review rt74 V2D, prefix consistency (FAIL, PRE-EXISTING). The program's own
`from zpy62.b import one`: pycsl's resolver skips this directory's REGULAR package ./zpy62/ (no b.py) and
reads the --import-path copy multi_file_lib/r613y/X3/zpy62/b.py (`ensures \result == 1`). CPython stops at
./zpy62/ (sys.path[0]) and searches `zpy62.b` only there: `cd <tree root> && PYTHONPATH=<X3> python <this
file>` raises ModuleNotFoundError: No module named 'zpy62.b'. pycsl verified the program against a file
CPython never loads (SUCCESS at int74).
REFUSED: PYCSL-SEM-IMPORT-DEPENDENCY-SEARCH-ORDER (the prefix `zpy62` is a regular package that does not
hold the file pycsl read).
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613y/X3
from zpy62.b import one


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return one()


if __name__ == "__main__":
    print("result", g())
