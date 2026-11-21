r"""Test 10228 -- run #8 u55 (FAIL): `--verification-image` is a declared model, not an exemption.
The route #613 closure check still judges every root: a local re.py in the --import-path root shadows the
`re` that `json` imports. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW.
"""
# pycsl-expected: FAIL
# pycsl-flags: --verification-image test-suite/corpus --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/re
import json


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s = json.dumps("a")
    return 1
