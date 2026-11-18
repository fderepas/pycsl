r"""Test 10180 -- run #8 route #613 (FAIL): the program imports ONLY `json`; the import root holds a local `re.py`. CPython (PYTHONPATH = that root, as pycsl's root order assumes) runs it as the `re` of `json/decoder.py` / `encoder.py` / `scanner.py`, a file pycsl never reads while it keeps its `json.dumps` model. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW (program -> json -> re -> .../re.py).
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/re
import json


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s = json.dumps("a")
    return 1


if __name__ == "__main__":
    print("result", f())
