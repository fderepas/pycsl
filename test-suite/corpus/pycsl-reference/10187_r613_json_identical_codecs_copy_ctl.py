r"""Test 10187 -- run #8 route #613 (PASS): over-refusal CONTROL: the root holds a BYTE-IDENTICAL copy of the interpreter's `codecs.py` (imported by `json/__init__.py`): admitted at that closure node by the route #326 rule exactly as a direct `import codecs` is, so the file proves as without it.
"""
# pycsl-expected: PASS
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/same
import json


#@ ensures \result == True
#@ assigns \nothing
def same() -> bool:
    return json.dumps([1]) == json.dumps([1])


if __name__ == "__main__":
    print("result", same())
