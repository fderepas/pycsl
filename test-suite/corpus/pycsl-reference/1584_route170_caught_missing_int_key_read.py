r"""Test 1584 - ROUTE #170 (gen #29): the same with an int-keyed dict (`d[2]` on `{1: 1}`) PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {1: 1}
    try:
        v = d[2]
    except KeyError:
        return 9
    return v
