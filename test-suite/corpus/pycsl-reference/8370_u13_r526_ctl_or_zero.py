r"""Test 8370 -- route #526 (control, expected PASS): `-(d.get("k") or 0) + (d.get("j") or 1)` (`x or 0` is never None); CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    return -(d.get("k") or 0) + (d.get("j") or 1)
