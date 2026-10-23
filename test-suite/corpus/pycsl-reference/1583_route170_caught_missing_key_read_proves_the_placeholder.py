r"""Test 1583 - ROUTE #170 (gen #29): `d = {"a": 1}; try: v = d["b"] except KeyError: return 9; return v` PROVED `\result == 0` (CPython 9): the missing-key arm of a dict subscript read is a placeholder `0`, justified as dead only under `no_exception KeyError`, so the handler was erased. In a function with a KeyError-catching handler the arm now raises KeyError.
"""
# pycsl-expected: FAIL
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        v = d["b"]
    except KeyError:
        return 9
    return v
