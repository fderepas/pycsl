r"""Test 3293 — gen #37 dict-value-wall Step 1 / R2a (expected FAIL): FALSE twin of 3292: the read must NOT
answer the non-matching head binding. CPython "Valid", so `\result == "g1"` must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "g1"
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"prover-result": {"answer": "Valid", "goal": "g1"}}
    return (rec.get("prover-result") or {}).get("answer", "") or ""


if __name__ == "__main__":
    print(repr(answer()))
