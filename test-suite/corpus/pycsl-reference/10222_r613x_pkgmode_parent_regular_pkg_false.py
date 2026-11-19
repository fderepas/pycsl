r"""Test 10222 -- run #8 u55, review rt66 g08 (FAIL). Declared `--as-package-module test-suite/corpus`:
`python -m pycsl-reference.10222_...` first imports the PARENT package `pycsl-reference`. In
test-suite/corpus it is only a namespace portion, and the --import-path root (CPython: PYTHONPATH) holds a
REGULAR package of that name, which CPython takes instead: it runs that `__init__.py`, a file pycsl never
reads, and never this program. REFUSED: PYCSL-SEM-IMPORT-PACKAGE-MODE-PARENT.
"""
# pycsl-expected: FAIL
# pycsl-flags: --as-package-module test-suite/corpus --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613x/g08


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


if __name__ == "__main__":
    print("result", f())
