r"""Test 3630 -- gen #37 route #302 (expected FAIL): a plain-name for-target over a `List[str]` parameter, read AFTER the loop (`x = ""; for x in e: pass; return x`) kept its PRE-loop value (route #36 wrote back only index/int loops), so `\result == ""` PROVED; CPython g(["a"]) == "a". Fixed by the route #302 write-back.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 1
#@ ensures \result == ""
#@ assigns \nothing
def g(e: List[str]) -> str:
    x = ""
    for x in e:
        pass
    return x

if __name__ == "__main__":
    assert g(["a"]) == "a"
