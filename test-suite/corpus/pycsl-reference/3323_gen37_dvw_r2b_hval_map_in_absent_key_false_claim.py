r"""Test 3323 — gen #37 dict-value-wall Step 2 / R2b (expected FAIL): FALSE twin of 3322: `"nope" in inner` is False in CPython; claiming True must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def has_loc() -> bool:
    rec: Dict[str, PyVal] = {"term": {"loc": 3, "x": 1}}
    inner = rec.get("term") or {}
    return "nope" in inner


if __name__ == "__main__":
    print(repr(has_loc()))
