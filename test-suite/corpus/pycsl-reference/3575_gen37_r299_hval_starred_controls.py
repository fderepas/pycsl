r"""Test 3575 -- gen #37 route #299 (expected PASS): CONTROLS: a plain hval list literal keeps its exact length / truthiness / membership, and a starred one is still a list (isinstance stays decided).
"""
# pycsl-expected: PASS
from typing import Any, List, Dict, Set, Tuple, Optional
PyVal = Any

#@ ensures \result == 3
#@ assigns \nothing
def plain_len() -> int:
    d: Dict[str, PyVal] = {"a": [1, 2, 3]}
    return len(d.get("a"))

#@ ensures \result == 1
#@ assigns \nothing
def plain_in() -> int:
    holder: Dict[str, PyVal] = {"r": {"f": ["q"]}}
    rec = holder.get("r")
    if "q" in rec["f"]:
        return 1
    return 2

#@ ensures \result == 1
#@ assigns \nothing
def starred_is_list() -> int:
    d: Dict[str, PyVal] = {"a": [*range(2), 3]}
    x = d.get("a")
    if isinstance(x, list):
        return 1
    return 2

if __name__ == "__main__":
    assert plain_len() == 3
    assert plain_in() == 1
    assert starred_is_list() == 1
