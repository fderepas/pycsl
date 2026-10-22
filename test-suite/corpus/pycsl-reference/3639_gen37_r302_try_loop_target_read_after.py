r"""Test 3639 -- gen #37 route #302 (expected FAIL): the loop sits in a `try` body, target read after the `try`; kept `""`; CPython g(["a"]) == "a".
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 1
#@ ensures \result == ""
#@ assigns \nothing
def g(e: List[str]) -> str:
    x = ""
    try:
        for x in e:
            pass
    except ValueError:
        pass
    return x

if __name__ == "__main__":
    assert g(["a"]) == "a"
