r"""Test 3326 — gen #37 dict-value-wall Step 2 / R2b (expected FAIL): SENTINEL HONESTY: `for c in rec.get("s", [])` over a STR iterates its 3 chars in CPython (result 3). A length-0 sentinel for non-`HArr` carriers would PROVE `\result == 0`; the uninterpreted `hval_iter_len_other` must leave it UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def count_str() -> int:
    rec: Dict[str, PyVal] = {"s": "abc"}
    n = 0
    for c in rec.get("s", []):
        n = n + 1
    return n


if __name__ == "__main__":
    print(repr(count_str()))
