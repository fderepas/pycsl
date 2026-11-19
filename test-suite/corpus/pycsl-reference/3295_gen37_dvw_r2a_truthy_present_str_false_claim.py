r"""Test 3295 — gen #37 dict-value-wall Step 1 / R2a (expected FAIL): FALSE twin of 3294: "x" is truthy, so the literal
is NOT selected; `\result == "dflt"` must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "dflt"
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"name": "x"}
    return rec.get("name") or "dflt"


if __name__ == "__main__":
    print(repr(answer()))
