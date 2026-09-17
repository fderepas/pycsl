r"""Test 1620 - ROUTE #177 (gen #29): `[d[k] for k in ["a", "b"]]` on `d = {"a": 1}` under `#@ no_exception KeyError` PROVED (CPython KeyError): the comprehension lowered to an opaque `list_comp` value with no per-element obligation. A comprehension containing a raising operation for an active exception is now refused.
"""
# pycsl-expected: FAIL
from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    xs = [d[k] for k in ["a", "b"]]
    return 0
