r"""Test 10186 -- run #8 route #613 (PASS): over-refusal CONTROL: the root holds a bare directory `re/` (no `__init__`): a namespace portion, which CPython's PathFinder passes over for the stdlib's regular `re` package, so it is not a shadow and the file proves as without it.
"""
# pycsl-expected: PASS
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/ns
import json


#@ ensures \result == True
#@ assigns \nothing
def same() -> bool:
    return json.dumps([1]) == json.dumps([1])


if __name__ == "__main__":
    print("result", same())
