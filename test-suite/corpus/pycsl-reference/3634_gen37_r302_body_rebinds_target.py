r"""Test 3634 -- gen #37 route #302 (expected FAIL): the loop BODY re-binds its own target (`for x in e: x = "z"`) and the target is read after; the body store went to the inner shadow, so `\result == ""` PROVED; CPython g(["a"]) == "z". After: the stale-read loop binds the outer ref with no shadow.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 1
#@ ensures \result == ""
#@ assigns \nothing
def g(e: List[str]) -> str:
    x = ""
    for x in e:
        x = "z"
    return x

if __name__ == "__main__":
    assert g(["a"]) == "z"
