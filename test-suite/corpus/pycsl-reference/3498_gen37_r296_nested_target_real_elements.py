r"""Test 3498 — gen #37 route #296 (expected PASS): control: a nested `for x in row` over a pyval loop target iterates the REAL inner list
(`[["a"]]`), so `isinstance(x, str)` proves True. CPython: True.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def first_is_str() -> bool:
    holder: Dict[str, PyVal] = {"rows": [["a"]]}
    rows = holder.get("rows") or []
    for row in rows:
        for x in row:
            return isinstance(x, str)
    return True

if __name__ == "__main__":
    print(first_is_str())
