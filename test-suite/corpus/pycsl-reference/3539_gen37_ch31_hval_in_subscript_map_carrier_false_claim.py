r"""Test 3539 — gen #37 ch31 (expected FAIL): 3538 with `\result == 2`, false in CPython (1).
At 0f7cb454 pycsl reported "All contracts formally proven" on it (the `hval_str_mem` arm).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    holder: Dict[str, PyVal] = {"r": {"fields": {"a": 1}}}
    rec = holder.get("r")
    if "a" in rec["fields"]:
        return 1
    return 2


if __name__ == "__main__":
    print(g())
