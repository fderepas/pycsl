r"""Test 8372 -- route #521 (control, expected PASS): `v = d.get("k"); if v is None: return ""; return v + "x"`; CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, str]) -> str:
    v = d.get("k")
    if v is None:
        return ""
    return v + "x"
