r"""Test 3539 — gen #37 ch31 (expected FAIL): 3538 with `\result == 2`, the claim the
old `hval_str_mem` lowering made true: false in CPython.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    rec: Dict[str, PyVal] = {"fields": {"a": 1}}
    if "a" in rec["fields"]:
        return 1
    return 2


if __name__ == "__main__":
    print(g())
