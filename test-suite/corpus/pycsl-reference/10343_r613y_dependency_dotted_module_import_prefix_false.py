r"""Test 10343 -- run #8 u61, review rt74 V2D, the `import a.b` form (FAIL, PRE-EXISTING; rt74 w5). As 10340,
but the --import-path dependency r613y_depw5 does `import zpy61.b` and calls `zpy61.b.one()`. CPython
(PYTHONPATH = X2) runs ./zpy61_alt/b.py and prints "result 2"; pycsl verified X2/zpy61/b.py.
REFUSED: PYCSL-SEM-IMPORT-DEPENDENCY-SEARCH-ORDER (the prefix `zpy61`).
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613y/X2
from r613y_depw5 import f


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()


if __name__ == "__main__":
    print("result", g())
