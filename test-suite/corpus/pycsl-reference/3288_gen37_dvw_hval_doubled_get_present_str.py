r"""Test 3288 — gen #37 dict-value-wall (expected PASS): honest CONTROL for 3286/3287: a PRESENT
STRING value behind a non-matching key, `rec["a"].get("x")` over `{"a": {"x": "v", "y": "w"}}`, is
"v" (CPython). Needs the R2a key-equality spec (head binding is "y").
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "v"
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"a": {"x": "v", "y": "w"}}
    return rec["a"].get("x")


if __name__ == "__main__":
    assert answer() == "v"; print("ok")
