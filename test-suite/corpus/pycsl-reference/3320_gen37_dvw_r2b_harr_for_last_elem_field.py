r"""Test 3320 — gen #37 dict-value-wall Step 2 / R2b (expected PASS): an index loop over an `HArr` (`for f in rec.get("fns", [])`) reads the fields of the element at the LAST index: CPython "yes". Bound exactly `hval_list_len`, element `hval_list_nth`; the `HNil -> HInt 0` sentinel is unreachable. Fails at base (L3-tc: `iter_length` wants int). Twin: 3321.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any

#@ ensures \result == "yes" or \result == "none"
#@ assigns \nothing
def find_last() -> str:
    rec: Dict[str, PyVal] = {"fns": [{"name": "b", "k": "y"}, {"name": "c", "k": "z"}]}
    for f in rec.get("fns", []):
        if f.get("k") == "z":
            if f.get("name") == "c":
                return "yes"
            return "no"
    return "none"


if __name__ == "__main__":
    assert find_last() == "yes"; print("ok")
