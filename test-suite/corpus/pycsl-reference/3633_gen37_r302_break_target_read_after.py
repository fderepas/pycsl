r"""Test 3633 -- gen #37 route #302 (expected FAIL): a loop left by `break`, target read after, kept the pre-loop `""`; CPython g(["a", "b"]) == "a".
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 2
#@ ensures \result == ""
#@ assigns \nothing
def g(e: List[str]) -> str:
    x = ""
    for x in e:
        if len(x) >= 0:
            break
    return x

if __name__ == "__main__":
    assert g(["a", "b"]) == "a"
