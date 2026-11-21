r"""Test 3572 -- gen #37 route #299 (expected FAIL): `"q" in [*"q"]` (nested hval list) is True in CPython; the claim it is absent is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional
PyVal = Any

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    holder: Dict[str, PyVal] = {"r": {"f": [*"q"]}}
    rec = holder.get("r")
    if "q" in rec["f"]:
        return 1
    return 2

if __name__ == "__main__":
    assert g() != 2, g()
