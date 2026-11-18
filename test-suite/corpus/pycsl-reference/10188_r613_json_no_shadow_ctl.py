r"""Test 10188 -- run #8 route #613 over-refusal CONTROL (PASS): `json` with NO local shadow in any root (the repo-root `json/` copy, admitted by route #326, is the only stdlib-named entry when cwd is the tree root): the file proves exactly as at base.
"""
# pycsl-expected: PASS
import json


#@ ensures \result == True
#@ assigns \nothing
def same() -> bool:
    return json.dumps([1]) == json.dumps([1])


if __name__ == "__main__":
    print("result", same())
