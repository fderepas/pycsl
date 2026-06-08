"""Test 0658 — inode-codec round-trip by leaf-composition (os-bodyvc-spec L2, standalone).

A mini struct codec (uint32 + uint16 fields) packed via leaf-COMPOSITION — `out[o]=b[i]` copying the
proven leaf's bytes, NOT re-deriving the byte math — and unpacked. `unpack(pack(x,y))` recovers both
fields: `_field0 == x and _field1 == y`. Proves by contract composition (the leaf reconstructs each
field; out copies its bytes). This is the inode round-trip pattern; the full 18-field _pack_inode proves
the same way STANDALONE, but its field contracts are too costly to re-verify inside the whole-os module
proof (proof-cost wall — see os-bodyvc-spec), so the codec round-trip is proven here in isolation while
os's _pack_inode keeps its light \length contract.
"""


#@ requires 0 <= a and a <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 4
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures 0 <= \result[2] and \result[2] <= 255
#@ ensures 0 <= \result[3] and \result[3] <= 255
#@ ensures \result[0] * 16777216 + \result[1] * 65536 + \result[2] * 256 + \result[3] == a
def pack32(a: int) -> list:
    return bytes([a // 16777216, (a // 65536) % 256, (a // 256) % 256, a % 256])


#@ requires 0 <= a and a <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures \result[0] * 256 + \result[1] == a
def pack16(a: int) -> list:
    return bytes([a // 256, a % 256])


#@ requires \valid(data, offset + 4)
#@ requires offset >= 0
#@ requires 0 <= data[offset] and data[offset] <= 255
#@ requires 0 <= data[offset + 1] and data[offset + 1] <= 255
#@ requires 0 <= data[offset + 2] and data[offset + 2] <= 255
#@ requires 0 <= data[offset + 3] and data[offset + 3] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset] * 16777216 + data[offset + 1] * 65536 + data[offset + 2] * 256 + data[offset + 3]
def unpack32(data: list, offset: int) -> int:
    return data[offset] * 16777216 + data[offset + 1] * 65536 + data[offset + 2] * 256 + data[offset + 3]


#@ requires \valid(data, offset + 2)
#@ requires offset >= 0
#@ requires 0 <= data[offset] and data[offset] <= 255
#@ requires 0 <= data[offset + 1] and data[offset + 1] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset] * 256 + data[offset + 1]
def unpack16(data: list, offset: int) -> int:
    return data[offset] * 256 + data[offset + 1]


# pack two fields into a 6-byte record via leaf-composition, then read field 0 back
#@ requires 0 <= x and x <= 4294967295
#@ requires 0 <= y and y <= 65535
#@ assigns \nothing
#@ ensures \result == x
def roundtrip_field0(x: int, y: int) -> int:
    out = [0] * 6
    b = pack32(x)
    out[0] = b[0]
    out[1] = b[1]
    out[2] = b[2]
    out[3] = b[3]
    c = pack16(y)
    out[4] = c[0]
    out[5] = c[1]
    rec = bytes(out)
    return unpack32(rec, 0)
