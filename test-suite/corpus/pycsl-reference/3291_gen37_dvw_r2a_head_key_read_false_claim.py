r"""Test 3291 — gen #37 dict-value-wall Step 1 / R2a (expected FAIL): FALSE twin of 3290. CPython returns "Valid", so
`\result == "Invalid"` must stay UNPROVED (z3 must not separate it the wrong way: the spec only
equates EQUAL strings).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "Invalid"
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"prover-result": {"answer": "Valid"}}
    return (rec.get("prover-result") or {}).get("answer", "") or ""


if __name__ == "__main__":
    print(repr(answer()))
