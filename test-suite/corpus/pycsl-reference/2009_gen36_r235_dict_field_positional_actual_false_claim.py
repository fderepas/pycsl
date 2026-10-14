r"""Test 2009 — route #235 (expected FAIL): a `Dict[int, int]` dataclass field built from a
SUPPLIED actual `m` with `1 in m`. At base the field took the DEFINITE empty map
`(const None)` and `1 in e.d` was decided False, so `\result == 0` PROVED (CPython returns 1);
the field is now the polymorphic unconstrained `any_map` (route #86).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Entry:
    line: int
    d: Dict[int, int] = field(default_factory=dict)


#@ requires 1 in m
#@ ensures \result == 0
#@ assigns \nothing
def has(m: Dict[int, int]) -> int:
    e = Entry(1, m)
    if 1 in e.d:
        return 1
    return 0
