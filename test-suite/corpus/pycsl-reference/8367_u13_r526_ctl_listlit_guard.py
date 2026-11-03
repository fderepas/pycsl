r"""Test 8367 -- route #526 (control, expected PASS): `xs = [d.get("k")]; if xs[0] is not None: xs[0] + 1`; CPython never raises
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    xs = [d.get("k")]
    if xs[0] is not None:
        return xs[0] + 1
    return 0
