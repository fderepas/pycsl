r"""Test 10052 -- lvU none-default map parameter `x or {}` (expected FAIL): after `d = d or {}` a
key of the CALLER's dict is still present (CPython: `h({"a": 1})` is 1), so `\result == 0` is
false. The arm keeps `d`, it does not decide that `d` is empty. Control: 10050.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional


#@ ensures \result == 0
#@ assigns \nothing
def h(d: Optional[Dict[str, int]] = None) -> int:
    d = d or {}
    if "a" in d:
        return 1
    return 0


if __name__ == "__main__":
    r = h({"a": 1})
    print("VIOLATION contract" if r != 0 else "result", r)
