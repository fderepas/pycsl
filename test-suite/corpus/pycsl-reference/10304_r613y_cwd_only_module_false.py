r"""Test 10304 -- run #8 u58, review rt69 G7 / n24 (FAIL, PRE-EXISTING). `r613y_cwd_helperq` exists in pycsl's
working directory (the tree root, where every corpus sweep runs) with `ensures \result == 1`, and in the
--import-path root returning 2. CPython's script mode never searches the cwd: `cd <tree root> &&
PYTHONPATH=<that root> python <this file>` loads the --import-path copy and prints 2, while pycsl took the
cwd copy and PROVED `\result == 1` at int72. REFUSED: PYCSL-SEM-IMPORT-CWD-ROOT.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613y/g7
import r613y_cwd_helperq


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return r613y_cwd_helperq.one()


if __name__ == "__main__":
    print("result", f())
