r"""Test 10184 -- run #8 route #613 (FAIL): the root holds a SOURCELESS `re.pyc` (no `re.py`): CPython's FileFinder loads it for the `re` that `json` imports. The route #611 artifact rule, applied at that closure node. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW (PYCSL-SEM-IMPORT-NONSOURCE-ARTIFACT at node `re`).
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/pyc
import json


#@ ensures \result == True
#@ assigns \nothing
def same() -> bool:
    return json.dumps("a") == json.dumps("a")


if __name__ == "__main__":
    print("result", same())
