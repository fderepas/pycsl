r"""Test 3638 -- gen #37 route #302 (expected FAIL): the loop sits under an `if`, target read after the `if` (flow-aware: the If statement holds a loop on the name); kept `""`; CPython g(["a"], True) == "a".
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 1
#@ ensures \result == ""
#@ assigns \nothing
def g(e: List[str], c: bool) -> str:
    x = ""
    if c:
        for x in e:
            pass
    return x

if __name__ == "__main__":
    assert g(["a"], True) == "a"
