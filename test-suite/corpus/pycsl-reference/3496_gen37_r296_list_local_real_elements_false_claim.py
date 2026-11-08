r"""Test 3496 — gen #37 route #296 (expected FAIL): twin of 3495 with `[{"k": 1}]`: the real element is a dict, `isinstance(x, str)` is False.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def first_is_str() -> bool:
    holder: Dict[str, PyVal] = {"xs": [{"k": 1}]}
    xs = holder.get("xs") or []
    for x in xs:
        return isinstance(x, str)
    return True

if __name__ == "__main__":
    print(first_is_str())
