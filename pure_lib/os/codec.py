"""pure_lib/os/codec.py — the inode byte codec (direntry codec stays in os until G4), extracted into its own MINIMAL-context
module (09-0702-os-plan G0b). Here the inode round-trip proves INLINE (G0a, ~42s); the full
UnixInodeFileSystem imports these functions and sees only their narrow `#@ interface` (so the os
proof stays light), while the rich definitions + the round-trip are verified once, cheaply, here.
Soundness: this module is in the verification suite — the bodies are checked, not trusted."""

#@ requires 0 <= v and v <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures \result[0] * 256 + \result[1] == v
def _pack_uint16_be(v: int) -> list:
    return bytes([v // 256, v % 256])

#@ requires \valid(data, offset + 2)
#@ requires offset >= 0
#@ requires 0 <= data[offset] and data[offset] <= 255
#@ requires 0 <= data[offset + 1] and data[offset + 1] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset] * 256 + data[offset + 1]
#@ ensures 0 <= \result and \result <= 65535
def _unpack_uint16_be(data: list, offset: int) -> int:
    return data[offset] * 256 + data[offset + 1]

#@ requires 0 <= v and v <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 4
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures 0 <= \result[2] and \result[2] <= 255
#@ ensures 0 <= \result[3] and \result[3] <= 255
#@ ensures \result[0]*16777216 + \result[1]*65536 + \result[2]*256 + \result[3] == v
def _pack_uint32_be(v: int) -> list:
    return bytes([v // 16777216, (v // 65536) % 256, (v // 256) % 256, v % 256])

#@ requires \valid(data, offset + 4)
#@ requires offset >= 0
#@ requires 0 <= data[offset + 0] and data[offset + 0] <= 255
#@ requires 0 <= data[offset + 1] and data[offset + 1] <= 255
#@ requires 0 <= data[offset + 2] and data[offset + 2] <= 255
#@ requires 0 <= data[offset + 3] and data[offset + 3] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset]*16777216 + data[offset+1]*65536 + data[offset+2]*256 + data[offset+3]
#@ ensures 0 <= \result and \result <= 4294967295
def _unpack_uint32_be(data: list, offset: int) -> int:
    return data[offset]*16777216 + data[offset+1]*65536 + data[offset+2]*256 + data[offset+3]

#@ requires \valid(fields, 18)
#@ requires 0 <= fields[0] and fields[0] <= 4294967295
#@ for k in range(1, 6):
#@     requires 0 <= fields[k] and fields[k] <= 65535
#@ requires 0 <= fields[6] and fields[6] <= 4294967295
#@ requires 0 <= fields[7] and fields[7] <= 4294967295
#@ for k in range(8, 18):
#@     requires 0 <= fields[k] and fields[k] <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 64
#@ for i in range(0, 64):
#@     ensures 0 <= \result[i] and \result[i] <= 255
#@ ensures \result[0]*16777216 + \result[1]*65536 + \result[2]*256 + \result[3] == fields[0]
#@ ensures \result[4]*256 + \result[5] == fields[1]
#@ ensures \result[6]*256 + \result[7] == fields[2]
#@ ensures \result[8]*256 + \result[9] == fields[3]
#@ ensures \result[10]*256 + \result[11] == fields[4]
#@ ensures \result[12]*256 + \result[13] == fields[5]
#@ ensures \result[14]*16777216 + \result[15]*65536 + \result[16]*256 + \result[17] == fields[6]
#@ ensures \result[18]*16777216 + \result[19]*65536 + \result[20]*256 + \result[21] == fields[7]
#@ ensures \result[22]*16777216 + \result[23]*65536 + \result[24]*256 + \result[25] == fields[8]
#@ ensures \result[26]*16777216 + \result[27]*65536 + \result[28]*256 + \result[29] == fields[9]
#@ ensures \result[30]*16777216 + \result[31]*65536 + \result[32]*256 + \result[33] == fields[10]
#@ ensures \result[34]*16777216 + \result[35]*65536 + \result[36]*256 + \result[37] == fields[11]
#@ ensures \result[38]*16777216 + \result[39]*65536 + \result[40]*256 + \result[41] == fields[12]
#@ ensures \result[42]*16777216 + \result[43]*65536 + \result[44]*256 + \result[45] == fields[13]
#@ ensures \result[46]*16777216 + \result[47]*65536 + \result[48]*256 + \result[49] == fields[14]
#@ ensures \result[50]*16777216 + \result[51]*65536 + \result[52]*256 + \result[53] == fields[15]
#@ ensures \result[54]*16777216 + \result[55]*65536 + \result[56]*256 + \result[57] == fields[16]
#@ ensures \result[58]*16777216 + \result[59]*65536 + \result[60]*256 + \result[61] == fields[17]
#@ interface ensures \length(\result) == 64
def _pack_inode(fields: list) -> list:
    out = [0] * 64
    b0 = _pack_uint32_be(fields[0])
    out[0] = b0[0]
    out[1] = b0[1]
    out[2] = b0[2]
    out[3] = b0[3]
    b1 = _pack_uint16_be(fields[1])
    out[4] = b1[0]
    out[5] = b1[1]
    b2 = _pack_uint16_be(fields[2])
    out[6] = b2[0]
    out[7] = b2[1]
    b3 = _pack_uint16_be(fields[3])
    out[8] = b3[0]
    out[9] = b3[1]
    b4 = _pack_uint16_be(fields[4])
    out[10] = b4[0]
    out[11] = b4[1]
    b5 = _pack_uint16_be(fields[5])
    out[12] = b5[0]
    out[13] = b5[1]
    b6 = _pack_uint32_be(fields[6])
    out[14] = b6[0]
    out[15] = b6[1]
    out[16] = b6[2]
    out[17] = b6[3]
    b7 = _pack_uint32_be(fields[7])
    out[18] = b7[0]
    out[19] = b7[1]
    out[20] = b7[2]
    out[21] = b7[3]
    b8 = _pack_uint32_be(fields[8])
    out[22] = b8[0]
    out[23] = b8[1]
    out[24] = b8[2]
    out[25] = b8[3]
    b9 = _pack_uint32_be(fields[9])
    out[26] = b9[0]
    out[27] = b9[1]
    out[28] = b9[2]
    out[29] = b9[3]
    b10 = _pack_uint32_be(fields[10])
    out[30] = b10[0]
    out[31] = b10[1]
    out[32] = b10[2]
    out[33] = b10[3]
    b11 = _pack_uint32_be(fields[11])
    out[34] = b11[0]
    out[35] = b11[1]
    out[36] = b11[2]
    out[37] = b11[3]
    b12 = _pack_uint32_be(fields[12])
    out[38] = b12[0]
    out[39] = b12[1]
    out[40] = b12[2]
    out[41] = b12[3]
    b13 = _pack_uint32_be(fields[13])
    out[42] = b13[0]
    out[43] = b13[1]
    out[44] = b13[2]
    out[45] = b13[3]
    b14 = _pack_uint32_be(fields[14])
    out[46] = b14[0]
    out[47] = b14[1]
    out[48] = b14[2]
    out[49] = b14[3]
    b15 = _pack_uint32_be(fields[15])
    out[50] = b15[0]
    out[51] = b15[1]
    out[52] = b15[2]
    out[53] = b15[3]
    b16 = _pack_uint32_be(fields[16])
    out[54] = b16[0]
    out[55] = b16[1]
    out[56] = b16[2]
    out[57] = b16[3]
    b17 = _pack_uint32_be(fields[17])
    out[58] = b17[0]
    out[59] = b17[1]
    out[60] = b17[2]
    out[61] = b17[3]
    return bytes(out)

#@ requires \valid(data, 64)
#@ for i in range(0, 64):
#@     requires 0 <= data[i] and data[i] <= 255
#@ assigns \nothing
#@ ensures \length(\result) == 18
#@ ensures \result[0] == data[0]*16777216 + data[1]*65536 + data[2]*256 + data[3]
#@ ensures \result[1] == data[4]*256 + data[5]
#@ ensures \result[2] == data[6]*256 + data[7]
#@ ensures \result[3] == data[8]*256 + data[9]
#@ ensures \result[4] == data[10]*256 + data[11]
#@ ensures \result[5] == data[12]*256 + data[13]
#@ ensures \result[6] == data[14]*16777216 + data[15]*65536 + data[16]*256 + data[17]
#@ ensures \result[7] == data[18]*16777216 + data[19]*65536 + data[20]*256 + data[21]
#@ ensures \result[8] == data[22]*16777216 + data[23]*65536 + data[24]*256 + data[25]
#@ ensures \result[9] == data[26]*16777216 + data[27]*65536 + data[28]*256 + data[29]
#@ ensures \result[10] == data[30]*16777216 + data[31]*65536 + data[32]*256 + data[33]
#@ ensures \result[11] == data[34]*16777216 + data[35]*65536 + data[36]*256 + data[37]
#@ ensures \result[12] == data[38]*16777216 + data[39]*65536 + data[40]*256 + data[41]
#@ ensures \result[13] == data[42]*16777216 + data[43]*65536 + data[44]*256 + data[45]
#@ ensures \result[14] == data[46]*16777216 + data[47]*65536 + data[48]*256 + data[49]
#@ ensures \result[15] == data[50]*16777216 + data[51]*65536 + data[52]*256 + data[53]
#@ ensures \result[16] == data[54]*16777216 + data[55]*65536 + data[56]*256 + data[57]
#@ ensures \result[17] == data[58]*16777216 + data[59]*65536 + data[60]*256 + data[61]
#@ interface ensures \length(\result) == 18
def _unpack_inode(data: list) -> list:
    fields = [0] * 18
    fields[0] = _unpack_uint32_be(data, 0)
    fields[1] = _unpack_uint16_be(data, 4)
    fields[2] = _unpack_uint16_be(data, 6)
    fields[3] = _unpack_uint16_be(data, 8)
    fields[4] = _unpack_uint16_be(data, 10)
    fields[5] = _unpack_uint16_be(data, 12)
    fields[6] = _unpack_uint32_be(data, 14)
    fields[7] = _unpack_uint32_be(data, 18)
    fields[8] = _unpack_uint32_be(data, 22)
    fields[9] = _unpack_uint32_be(data, 26)
    fields[10] = _unpack_uint32_be(data, 30)
    fields[11] = _unpack_uint32_be(data, 34)
    fields[12] = _unpack_uint32_be(data, 38)
    fields[13] = _unpack_uint32_be(data, 42)
    fields[14] = _unpack_uint32_be(data, 46)
    fields[15] = _unpack_uint32_be(data, 50)
    fields[16] = _unpack_uint32_be(data, 54)
    fields[17] = _unpack_uint32_be(data, 58)
    return fields

# Round-trip proof (G0a): unpack(pack(fields)) reconstructs every field — proves INLINE here.
#@ requires \valid(fields, 18)
#@ requires 0 <= fields[0] and fields[0] <= 4294967295
#@ for k in range(1, 6):
#@     requires 0 <= fields[k] and fields[k] <= 65535
#@ requires 0 <= fields[6] and fields[6] <= 4294967295
#@ requires 0 <= fields[7] and fields[7] <= 4294967295
#@ for k in range(8, 18):
#@     requires 0 <= fields[k] and fields[k] <= 4294967295
#@ assigns \nothing
#@ ensures \result[0] == fields[0]
#@ ensures \result[1] == fields[1]
#@ ensures \result[2] == fields[2]
#@ ensures \result[3] == fields[3]
#@ ensures \result[4] == fields[4]
#@ ensures \result[5] == fields[5]
#@ ensures \result[6] == fields[6]
#@ ensures \result[7] == fields[7]
#@ ensures \result[8] == fields[8]
#@ ensures \result[9] == fields[9]
#@ ensures \result[10] == fields[10]
#@ ensures \result[11] == fields[11]
#@ ensures \result[12] == fields[12]
#@ ensures \result[13] == fields[13]
#@ ensures \result[14] == fields[14]
#@ ensures \result[15] == fields[15]
#@ ensures \result[16] == fields[16]
#@ ensures \result[17] == fields[17]
def _inode_round_trip(fields: list) -> list:
    packed = _pack_inode(fields)
    return _unpack_inode(packed)
