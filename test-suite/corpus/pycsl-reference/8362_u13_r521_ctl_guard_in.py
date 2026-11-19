r"""Test 8362 -- route #521 (control, expected PASS): `v is not None and v in "ab"`; CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, str]) -> int:
    v = d.get("k")
    if v is not None and v in "ab":
        return 1
    return 0
