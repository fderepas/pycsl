r"""Test 8367 -- route #526 (control, expected PASS): `xs = [d.get("k")]; v = xs[0]; if v is not None: v + 1`; CPython never raises. (Integration note, driver run #4: the original `if xs[0] is not None: xs[0] + 1` is REFUSED once route #527 (u15) lands beside #526 -- #527 judges the subscript operand and route #432's narrowing does not narrow a subscript expression; fail-closed over-refusal recorded in route526 / route527.)
"""
# pycsl-expected: PASS
from typing import Dict, List, Optional
from dataclasses import dataclass


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    xs = [d.get("k")]
    v = xs[0]
    if v is not None:
        return v + 1
    return 0
