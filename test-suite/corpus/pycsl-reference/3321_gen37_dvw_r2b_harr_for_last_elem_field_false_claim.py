r"""Test 3321 — gen #37 dict-value-wall Step 2 / R2b (expected FAIL): FALSE twin of 3320: claims the last element has the wrong name ("no"); CPython "yes", so it must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == "no" or \result == "none"
#@ assigns \nothing
def find_last() -> str:
    rec: Dict[str, PyVal] = {"fns": [{"name": "b", "k": "y"}, {"name": "c", "k": "z"}]}
    for f in rec.get("fns", []):
        if f.get("k") == "z":
            if f.get("name") == "c":
                return "yes"
            return "no"
    return "none"


if __name__ == "__main__":
    print(repr(find_last()))
