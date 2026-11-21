r"""Test 3490 — gen #37 route #296 (expected FAIL): the route witness. `xs = d.get("xs") or []` is a LIST carrier; a bare `for x in xs` iterated it
as dict KEYS (arbitrary strings), so `isinstance(x, str)` proved True. CPython: False.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def first_is_str(d: Dict[str, PyVal]) -> bool:
    xs = d.get("xs") or []
    for x in xs:
        return isinstance(x, str)
    return True

if __name__ == "__main__":
    print(first_is_str({"xs": [{"k": 1}]}))
