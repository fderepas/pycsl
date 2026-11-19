r"""Test 3495 — gen #37 route #296 (expected PASS): control: a bare `for x in xs` over a KNOWN list carrier iterates its REAL elements (R2b
`hval_list_nth`), so `isinstance(x, str)` on `["a", "b"]` proves True. CPython: True.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def first_is_str() -> bool:
    holder: Dict[str, PyVal] = {"xs": ["a", "b"]}
    xs = holder.get("xs") or []
    for x in xs:
        return isinstance(x, str)
    return True

if __name__ == "__main__":
    print(first_is_str())
