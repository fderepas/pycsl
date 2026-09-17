r"""Test 1585 - ROUTE #170 (gen #29): the same under `except Exception` PROVED `\result == 0` (CPython 9); the raising arm is now refused (KeyError is not declared under the broader handler).
"""
# pycsl-expected: FAIL
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        v = d["b"]
    except Exception:
        return 9
    return v
