r"""Test 10180 -- run #8 route #613 (FAIL): the program imports ONLY `json`; the import root holds a local `re.py`. CPython (PYTHONPATH = that root, as pycsl's root order assumes) runs it as the `re` of `json/decoder.py` / `encoder.py` / `scanner.py`, a file pycsl never reads while it keeps its `json.dumps` model. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW (program -> json -> re -> .../re.py).
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/re
import json


#@ ensures \result == True
#@ assigns \nothing
def same() -> bool:
    return json.dumps([1]) == json.dumps([1])


if __name__ == "__main__":
    print("result", same())
