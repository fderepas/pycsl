r"""Test 1625 - ROUTE #178 (gen #29): `v = get(d)` with `def get(d): return d["b"]` on `d = {"a": 1}` under the CALLER's `#@ no_exception KeyError` PROVED (CPython KeyError): inside the uncontracted helper the missing-key read is the ambient placeholder. A call to same-file code with an unmodelled implicit raise for an active exception is now refused.
"""
# pycsl-expected: FAIL
from typing import Dict
_ = 0  # anchor


def get(d: Dict[str, int]) -> int:
    return d["b"]


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    v = get(d)
    return v * 0
