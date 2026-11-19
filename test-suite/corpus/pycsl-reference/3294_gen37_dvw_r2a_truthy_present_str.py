r"""Test 3294 — gen #37 dict-value-wall Step 1 / R2a (expected PASS): truthiness of a PRESENT non-empty HStr.
`rec.get("name") or "dflt"` over `{"name": "x"}` keeps "x" (CPython). `hval_truthy (HStr s)` is
`not (hpairs_key_eq s "")`, undecidable before R2a. Twin: 3295.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "x"
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"name": "x"}
    return rec.get("name") or "dflt"


if __name__ == "__main__":
    assert answer() == "x"; print("ok")
