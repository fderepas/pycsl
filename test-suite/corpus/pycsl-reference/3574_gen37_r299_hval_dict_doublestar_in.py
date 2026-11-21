r"""Test 3574 -- gen #37 route #299 (expected FAIL): a `**m` entry of a dict literal stored as an hval splices m: with m = {"k": 1}, `"k" in d.get("a")` is True in CPython; the claim it is absent is FALSE.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional
PyVal = Any

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    m: Dict[str, PyVal] = {"k": 1}
    d: Dict[str, PyVal] = {"a": {**m, "b": 1}}
    if "k" in d.get("a"):
        return 1
    return 2

if __name__ == "__main__":
    assert g() != 2, g()
