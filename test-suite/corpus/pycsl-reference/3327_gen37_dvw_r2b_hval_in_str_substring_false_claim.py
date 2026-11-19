r"""Test 3327 — gen #37 dict-value-wall Step 2 / R2b (expected FAIL): SENTINEL HONESTY: `"b" in s` where `s` is an hval STR is substring containment in CPython (True). The membership arm maps a non-dict/non-list carrier to the UNINTERPRETED `hval_in_other`, never a constant False, so `\result == False` must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == False
#@ assigns \nothing
def in_str() -> bool:
    rec: Dict[str, PyVal] = {"s": "abc"}
    s = rec.get("s")
    return "b" in s


if __name__ == "__main__":
    print(repr(in_str()))
