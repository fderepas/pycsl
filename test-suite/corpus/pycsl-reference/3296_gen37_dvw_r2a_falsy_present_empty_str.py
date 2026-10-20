r"""Test 3296 — gen #37 dict-value-wall Step 1 / R2a (expected PASS): a PRESENT EMPTY HStr is falsy: `rec.get("name") or
"dflt"` over `{"name": ""}` is "dflt" (CPython). Needs `hpairs_key_eq "" ""` = true. Twin: 3297.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "dflt"
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"name": ""}
    return rec.get("name") or "dflt"


if __name__ == "__main__":
    assert answer() == "dflt"; print("ok")
