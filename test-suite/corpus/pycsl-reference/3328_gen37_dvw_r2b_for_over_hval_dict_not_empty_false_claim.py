r"""Test 3328 — gen #37 dict-value-wall Step 2 / R2b (expected FAIL): SENTINEL HONESTY: `for k in rec.get("d", [])` over a DICT iterates its 1 key in CPython (result 1). The non-`HArr` carrier iterates the UNINTERPRETED `hval_iter_len_other`, so `\result == 0` must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def count_dict() -> int:
    rec: Dict[str, PyVal] = {"d": {"a": 1}}
    n = 0
    for k in rec.get("d", []):
        n = n + 1
    return n


if __name__ == "__main__":
    print(repr(count_dict()))
