r"""Test 3388 -- route #289 (expected PASS): CONTROLS: an element store through the list's OWN name beside a scalar tuple, keeps PROVING.
"""
# pycsl-expected: PASS
from typing import List, Tuple


#@ ensures \result == 5
def own_name_store() -> int:
    a: List[int] = [1]
    t: Tuple[int, int] = (a[0], 7)
    a[0] = 5
    return a[0]


if __name__ == "__main__":
    assert own_name_store() == 5
