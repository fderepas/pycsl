r"""Test 3322 — gen #37 dict-value-wall Step 2 / R2b (expected PASS): `"loc" in inner` over an hval dict (`HMap`) is key presence, `pairs_get <> None` over the R2a key equality: CPython True. Fails at base (L3-tc). Twin: 3323.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def has_loc() -> bool:
    rec: Dict[str, PyVal] = {"term": {"loc": 3, "x": 1}}
    inner = rec.get("term") or {}
    return "loc" in inner


if __name__ == "__main__":
    assert has_loc() is True; print("ok")
