r"""Test 3637 -- gen #37 route #302 (expected FAIL): a `for x in sorted(e)` loop over ints (not the `array int` PARAMETER case #36 covered), target read after, kept 0; CPython g([4]) == 4.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(e) == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(e: List[int]) -> int:
    x = 0
    for x in sorted(e):
        pass
    return x

if __name__ == "__main__":
    assert g([4]) == 4
