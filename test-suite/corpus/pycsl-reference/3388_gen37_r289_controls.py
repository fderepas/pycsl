r"""Test 3388 -- route #289 (expected PASS): CONTROLS: an element store through the list's OWN name beside a scalar tuple, and reading a scalar tuple element, keep PROVING.
"""
# pycsl-expected: PASS
from typing import List, Tuple


#@ ensures \result == 5
def own_name_store() -> int:
    a: List[int] = [1]
    t: Tuple[int, int] = (a[0], 7)
    a[0] = 5
    return a[0]


#@ ensures \result == 7
def scalar_element() -> int:
    t: Tuple[int, int] = (3, 7)
    return t[1]


if __name__ == "__main__":
    assert own_name_store() == 5
    assert scalar_element() == 7
