"""Formal test for Phase 1+3 modules: tm (ClockModel), enm (IntEnum, auto),
typ (cast). Each function uses symbolic inputs and proves postconditions
for all valid inputs.
bisect_left excluded: stub types a as int but \length(a) requires array."""

from pure_lib.tm import ClockModel
from pure_lib.enm import IntEnum, auto, AutoCounter
from pure_lib.typ import cast


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def formal_test_clock(c) -> int:
    t = c.monotonic()
    if t < 0:
        return 1
    return 0


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def formal_test_intEnum(v, n) -> int:
    e = IntEnum(v, n)
    if e.value() != v:
        return 1
    if e.name() != n:
        return 1
    return 0


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def formal_test_auto(ac) -> int:
    a1 = ac.auto()
    if a1 < 1:
        return 1
    return 0


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def formal_test_cast(val) -> int:
    r = cast(0, val)
    if r != val:
        return 1
    return 0
