r"""Test 3285 — gen #37 dict-value-wall Step 0, R6 (expected PASS): honest CONTROL for 3283/3284.
The value is the INT 0 (falsy), so `rec.get("answer") or "none"` is the literal "none" (CPython
"none"). The repair keeps the falsy-operand arm: a falsy hval selects the literal.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "none"
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"answer": 0}
    return rec.get("answer") or "none"


if __name__ == "__main__":
    assert answer() == "none"
    print("ok")
