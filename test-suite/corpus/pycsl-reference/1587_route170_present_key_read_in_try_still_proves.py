r"""Test 1587 - ROUTE #170 control (gen #29): a PRESENT key read inside the same `try` still proves `\result == 1`.
"""
from typing import Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        v = d["a"]
    except KeyError:
        return 9
    return v
