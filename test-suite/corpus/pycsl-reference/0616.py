"""Test 0616 — faithful bytes()/bytearray() constructors (07-1321 S1).

`bytes(x)`/`bytearray(x)` lower to an `array int` constructor whose contract is LENGTH- and
ELEMENT-preserving (no-more-int doctrine), so a packing function proves `\length(\result)` and a
later byte read proves the element value. `bytearray()` is an empty (length-0) buffer. Previously
these hit the unannotated-callee fallback and were typed `int -> int`.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \length(\result) == 3
#@ assigns \nothing
def mk() -> list:
    return bytes([1, 2, 3])


#@ ensures \length(\result) == 0
#@ assigns \nothing
def empty() -> list:
    return bytearray()


#@ ensures \result == 1
#@ assigns \nothing
def first() -> int:
    b = bytes([1, 2, 3])
    return b[0]
