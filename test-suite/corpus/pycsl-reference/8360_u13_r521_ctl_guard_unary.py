r"""Test 8360 -- route #521 (control, expected PASS): `v = d.get("k"); if v is not None: return -v` (the guard discharges the obligation); CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    v = d.get("k")
    if v is not None:
        return -v
    return 0
