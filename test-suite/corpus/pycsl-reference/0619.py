"""Test 0619 — `array += array` routes to array-extend, not integer `+` (07-1321 S4).

Python `a += b` on lists is concatenation. The emitter now recognises a list/bytes/bytearray
param that is a `+=` target as array-typed and lowers to `array_extend` (dereferencing a
ref-wrapped target), so it type-checks as an `array int` operation instead of mis-lowering to
integer `+` (an `array int` vs `int` error). (Faithful length-additive concatenation is a
documented follow-on; this test pins the no-int-leak / type-correct behaviour.)
"""
# pycsl-flags: --memory-model hoare


#@ requires \length(a) >= 0 and \length(b) >= 0
#@ assigns \nothing
def cat(a: list, b: list) -> list:
    a += b
    return a
