r"""Test 10331 -- run #8 u60, review rt72 A1 (FAIL, PRE-EXISTING; the a1x shape). The program imports
r613z_depx from the --import-path root multi_file_lib/r613z/X (CPython: PYTHONPATH); r613z_depx's absolute
`from r613z_two import one` resolved, for pycsl, from X (X/r613z_two.py, `ensures \result == 1`). CPython's
sys.path is [this directory, X, ...]: `cd <tree root> && PYTHONPATH=<X> python <this file>` loads
./r613z_two.py and prints "result 2". pycsl PROVED `\result == 1` at int73.
REFUSED: PYCSL-SEM-IMPORT-DEPENDENCY-SEARCH-ORDER.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613z/X
from r613z_depx import f


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()


if __name__ == "__main__":
    print("result", g())
