r"""Test 10183 -- run #8 route #613 (FAIL): the root holds a local `sitecustomize.py`: not a standard-library name, but one the stdlib itself imports (`site.py`, at interpreter startup), and with the root on sys.path (PYTHONPATH, the root order pycsl assumes) CPython runs it (measured, witnesses-r613/cpython.txt); no model of pycsl assumes it. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/nonstd
import json


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s = json.dumps("a")
    return 1


if __name__ == "__main__":
    print("result", f())
