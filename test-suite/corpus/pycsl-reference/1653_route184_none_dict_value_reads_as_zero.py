r"""Test 1653 - ROUTE #184 (gen #29): `d: Dict[str, Optional[int]] = {"a": None}` stored the integer 0, so `d["a"] == 0` PROVED True (CPython False). The `None` value now stores the opaque `pycsl_none`.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    d: Dict[str, Optional[int]] = {"a": None}
    return d["a"] == 0
