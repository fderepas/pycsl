"""Test 0655 — L0 (os-bodyvc-spec): contract `\result[i]` over an array result is a real Array.get.

A value postcondition relating the bytes of a packed result to the input — `\result[0]*256 +
\result[1] == v` — proves. Previously `\result[i]` in an `ensures` lowered to the OPAQUE
`subscript_get result i` (uninterpreted), so no value property over an array result could be expressed
or proven; now it lowers to `result[i]` (Array.get). This is the leaf-first foundation for byte
pack/unpack contracts. (Contract grammar has no `<<`; `*256` is the equivalent. Arithmetic body
`v//256, v%256` == bitwise `(v>>8)&0xFF` for 0<=v<=0xFFFF and is provable.)
"""


#@ requires 0 <= v and v <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures \result[0] * 256 + \result[1] == v
def pack_uint16_be(v: int) -> list:
    return bytes([v // 256, v % 256])
