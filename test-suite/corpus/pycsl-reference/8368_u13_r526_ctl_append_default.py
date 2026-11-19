r"""Test 8368 -- route #526 (control, expected PASS): `xs.append(d.get("k", 0)); xs[1] + 1`; CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    xs = [1]
    xs.append(d.get("k", 0))
    return xs[1] + 1
