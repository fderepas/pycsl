r"""Test 1623 - ROUTE #177 (gen #29): `{k: d[k] for k in ["b"]}` on `d = {"a": 1}` under `#@ no_exception KeyError` PROVED (CPython KeyError).
"""
# pycsl-expected: FAIL
from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    e = {k: d[k] for k in ["b"]}
    return 0
