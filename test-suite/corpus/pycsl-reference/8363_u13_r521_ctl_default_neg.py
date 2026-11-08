r"""Test 8363 -- route #521 (control, expected PASS): `-d.get("k", 0)` (a non-None default is never None); CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    return -d.get("k", 0)
