r"""Test 3636 -- gen #37 route #302 (expected FAIL): a `range(5, 0, -1)` loop (its element is not the bare counter, so route #36's index write-back did not fire), target read after, kept 0; CPython g() == 1.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    i = 0
    for i in range(5, 0, -1):
        pass
    return i

if __name__ == "__main__":
    assert g() == 1
