r"""Test 3499 — gen #37 route #296 (expected FAIL): twin of 3498 with `[[1]]`: the inner element is an int, `isinstance(x, str)` is False.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def first_is_str() -> bool:
    holder: Dict[str, PyVal] = {"rows": [[1]]}
    rows = holder.get("rows") or []
    for row in rows:
        for x in row:
            return isinstance(x, str)
    return True

if __name__ == "__main__":
    print(first_is_str())
