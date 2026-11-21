r"""Test 3497 — gen #37 route #296 (expected PASS): control: a bare `for k in m` over an `HMap` carrier still takes the dict-KEY view (per carrier,
inside the R2b match), so `isinstance(k, str)` proves True. CPython: True.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def first_key_is_str() -> bool:
    holder: Dict[str, PyVal] = {"m": {"a": 1}}
    m = holder.get("m") or {}
    for k in m:
        return isinstance(k, str)
    return True

if __name__ == "__main__":
    print(first_key_is_str())
