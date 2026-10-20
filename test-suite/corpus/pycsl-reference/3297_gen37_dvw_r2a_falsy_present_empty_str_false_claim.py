r"""Test 3297 — gen #37 dict-value-wall Step 1 / R2a (expected FAIL): FALSE twin of 3296: CPython "dflt", so
`\result == ""` must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"name": ""}
    return rec.get("name") or "dflt"


if __name__ == "__main__":
    print(repr(answer()))
