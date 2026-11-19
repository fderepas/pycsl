r"""Test 10220 -- run #8 u55, review rt66 g02 (FAIL). Declared `--as-package-module test-suite/corpus`:
the program runs as `cd test-suite/corpus && python -m pycsl-reference.10220_...`, so CPython's sys.path[0]
is test-suite/corpus and `import r613x_g02` loads test-suite/corpus/r613x_g02.py (returns 2), while
pycsl's resolution (program directory, cwd, ..., --import-path) took the --import-path copy (returns 1)
and PROVED `\result == 1` at ff03f178c. REFUSED: PYCSL-SEM-IMPORT-PACKAGE-MODE-ORDER.
"""
# pycsl-expected: FAIL
# pycsl-flags: --as-package-module test-suite/corpus --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613x/g02
import r613x_g02


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return r613x_g02.one()


if __name__ == "__main__":
    print("result", f())
