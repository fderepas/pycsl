r"""Test 3325 — gen #37 dict-value-wall Step 2 / R2b (expected FAIL): FALSE twin of 3324: `"z" in names` is False in CPython; claiming True must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def has_name() -> bool:
    rec: Dict[str, PyVal] = {"names": ["a", "x"]}
    names = rec.get("names") or []
    return "z" in names


if __name__ == "__main__":
    print(repr(has_name()))
