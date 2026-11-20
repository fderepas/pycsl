r"""Test 10224 -- run #8 u55, review rt66 g10 (FAIL). `import json` with a NON-identical json.py in an
--import-path root. With cwd = the tree root, pycsl's first hit for `json` is the admitted ./json/ copy, so
the --import-path file was never judged; CPython with PYTHONPATH = that root (script mode: cwd is not on
sys.path) loads it. Every candidate is now judged in its own root. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613x/g10
import json


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s = json.dumps("a")
    return 1


if __name__ == "__main__":
    print("result", f())
