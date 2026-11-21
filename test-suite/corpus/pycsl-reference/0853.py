"""Test 0853 — WL-04g NEGATIVE lock (int+record mixed literal). # pycsl-expected: FAIL

A mixed `[1, Point(2, 3)]` literal has no faithful `array τ` element type: the int-coercion
default ill-typed the record element into an `array int` (silent Why3 TYPEERR). WL-04g makes
it FAIL CLOSED — PyCSL REJECTS the heterogeneous literal. No content claim about either the
int element or the record element may prove. If this reports Verification SUCCESS, the
boundary has regressed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \result == 0
def mixed_int_record_rejected() -> int:
    a = [1, Point(2, 3)]
    return a[0]
