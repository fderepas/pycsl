r"""Test 3090 — route #280 (expected FAIL): `d[0].pop()` became `pop_0 ()`, so `len(d[0]) == 1` PROVED
at 72ab1c57 (red-team p230). CPython: 0. Now refused.
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, List[int]] = {0: [7]}
    d[0].pop()
    return len(d[0])


if __name__ == "__main__":
    assert f() == 0
