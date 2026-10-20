r"""Test 3324 — gen #37 dict-value-wall Step 2 / R2b (expected PASS): `"x" in names` over an hval LIST (`HArr` of `HStr`) is element equality: CPython True. Fails at base (L3-tc). Twin: 3325.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def has_name() -> bool:
    rec: Dict[str, PyVal] = {"names": ["a", "x"]}
    names = rec.get("names") or []
    return "x" in names


if __name__ == "__main__":
    assert has_name() is True; print("ok")
