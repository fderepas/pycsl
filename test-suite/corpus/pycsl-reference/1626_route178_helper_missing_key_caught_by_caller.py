r"""Test 1626 - ROUTE #178 (gen #29): the same helper called inside `try ... except KeyError: return 9` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
from typing import Dict
_ = 0  # anchor


def get(d: Dict[str, int]) -> int:
    return d["b"]


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        v = get(d)
    except KeyError:
        return 9
    return v * 0
