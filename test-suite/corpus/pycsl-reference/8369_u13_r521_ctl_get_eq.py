r"""Test 8369 -- route #521 (control, expected PASS): `d.get("k") == 3` (equality never raises); CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    if d.get("k") == 3:
        return 1
    return 0
