r"""Test 10340 -- run #8 u61, review rt74 V2D (FAIL, PRE-EXISTING). The program imports r613y_depv2 from the
--import-path root multi_file_lib/r613y/X2 (CPython: PYTHONPATH); r613y_depv2's dotted absolute
`from zpy61.b import one` resolved, for pycsl, in BOTH views to X2/zpy61/b.py (`ensures \result == 1`):
pycsl's resolver skips the program directory's regular package ./zpy61/ (no b.py) and falls through.
CPython stops at ./zpy61/__init__.py (sys.path[0]), which redirects `__path__` to ./zpy61_alt:
`cd <tree root> && PYTHONPATH=<X2> python <this file>` loads ./zpy61_alt/b.py and prints "result 2".
REFUSED: PYCSL-SEM-IMPORT-DEPENDENCY-SEARCH-ORDER (the prefix `zpy61` is compared too).
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613y/X2
from r613y_depv2 import f


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()


if __name__ == "__main__":
    print("result", g())
