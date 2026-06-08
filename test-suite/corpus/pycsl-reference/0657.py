"""Test 0657 — L2 sub-gap 2 (os-bodyvc-spec): pack/unpack round-trip by contract composition.

`unpack16(pack16(x), 0) == x` proves purely from the leaves' VALUE contracts (L1) — no body tracking.
Previously the array-returning call `pack16(x)`, passed to unpack16's `array int` param, was clobbered
to a placeholder `(Array.make 1 0)` by the arg coercion (losing the value), so the round-trip couldn't
compose. The coercion now passes through a function-application arg `(pack16 x)`. This is the
foundation for the inode/direntry field-wise round-trip (an array-returning call composing into the
next layer's contract).
"""


#@ requires 0 <= a and a <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures \result[0] * 256 + \result[1] == a
def pack16(a: int) -> list:
    return bytes([a // 256, a % 256])


#@ requires \valid(data, offset + 2)
#@ requires offset >= 0
#@ requires 0 <= data[offset] and data[offset] <= 255
#@ requires 0 <= data[offset + 1] and data[offset + 1] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset] * 256 + data[offset + 1]
def unpack16(data: list, offset: int) -> int:
    return data[offset] * 256 + data[offset + 1]


#@ requires 0 <= x and x <= 65535
#@ assigns \nothing
#@ ensures \result == x
def roundtrip(x: int) -> int:
    return unpack16(pack16(x), 0)
